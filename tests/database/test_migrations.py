"""PostgreSQL integration tests. Set DB_TEST_ENABLE=1 for a disposable database."""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import unittest
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "contracts" / "database" / "migrate.py"
UP = ROOT / "contracts" / "database" / "migrations" / "0001_initial.up.sql"


class StaticSchemaTests(unittest.TestCase):
    def test_initial_reversible_migration_and_runner(self):
        self.assertTrue(UP.is_file())
        self.assertTrue(UP.with_name("0001_initial.down.sql").is_file())
        text = UP.read_text(encoding="utf-8")
        for table in ("users", "sessions", "friendships", "conversations",
                      "conversation_members", "messages", "outbox_events",
                      "plugin_artifacts", "plugin_instances", "plugin_kv"):
            self.assertRegex(text, rf"CREATE TABLE {table}\s*\(")
        self.assertIn("UNIQUE (conversation_id, request_id)", text)
        self.assertIn("UNIQUE (conversation_id, seq)", text)
        self.assertIn("PRIMARY KEY (user_id, client_type)", text)
        self.assertIn("PRIMARY KEY (user_low_id, user_high_id)", text)
        self.assertIn("UNIQUE (direct_user_low_id, direct_user_high_id)", text)

    def test_down_requires_explicit_data_loss_acknowledgement(self):
        result = subprocess.run([sys.executable, str(RUNNER), "down"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("--allow-data-loss", result.stderr)


@unittest.skipUnless(os.environ.get("DB_TEST_ENABLE") == "1", "set DB_TEST_ENABLE=1 with a disposable PostgreSQL database")
class PostgreSQLMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("psql"):
            raise unittest.SkipTest("psql unavailable")
        cls.schema = "db_test_" + uuid.uuid4().hex
        cls.env = os.environ.copy()
        cls.psql(f"CREATE SCHEMA {cls.schema};", env=cls.env)
        cls.env["PGOPTIONS"] = f"-c search_path={cls.schema}"

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "schema"):
            cls.psql(f"DROP SCHEMA {cls.schema} CASCADE;", env=os.environ.copy())

    @classmethod
    def psql(cls, sql, env=None):
        result = subprocess.run(["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t"],
                                input=sql, text=True, capture_output=True, env=env or cls.env)
        if result.returncode:
            raise AssertionError(result.stderr)
        return result.stdout.strip()

    def migrate(self, *args):
        result = subprocess.run([sys.executable, str(RUNNER), *args],
                                text=True, capture_output=True, env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_forward_uniqueness_and_rollback(self):
        self.migrate("up")
        self.assertIn("already applied", self.migrate("up"))
        self.assertIn("applied", self.migrate("status"))
        # Every rejected insert is executed in its own PL/pgSQL exception block;
        # the expected constraint error is caught without aborting the suite.
        sql = """
        INSERT INTO users(user_id, username, display_name, password_hash) VALUES
          ('00000000-0000-0000-0000-000000000001','alice','Alice','hashed'),
          ('00000000-0000-0000-0000-000000000002','bob','Bob','hashed');
        INSERT INTO sessions(user_id, client_type, session_id, session_epoch, refresh_token_hash, status, device_id, expires_at)
          VALUES ('00000000-0000-0000-0000-000000000001','WEB','00000000-0000-0000-0000-000000000011',1,'hashed','ACTIVE','browser',now()+interval '1 day');
        DO $$ BEGIN
          INSERT INTO sessions(user_id, client_type, session_id, session_epoch, refresh_token_hash, status, device_id, expires_at)
            VALUES ('00000000-0000-0000-0000-000000000001','WEB','00000000-0000-0000-0000-000000000012',2,'hashed','ACTIVE','browser',now()+interval '1 day');
          RAISE EXCEPTION 'duplicate session slot accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by)
          VALUES ('00000000-0000-0000-0000-000000000021','DIRECT','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001');
        DO $$ BEGIN
          INSERT INTO conversations(conversation_id,kind,direct_user_low_id,direct_user_high_id,created_by)
            VALUES ('00000000-0000-0000-0000-000000000022','DIRECT','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001');
          RAISE EXCEPTION 'duplicate direct pair accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        DO $$ BEGIN
          INSERT INTO conversations(conversation_id,kind,created_by)
            VALUES ('00000000-0000-0000-0000-000000000023','GROUP','00000000-0000-0000-0000-000000000001');
          RAISE EXCEPTION 'GROUP without create request accepted';
        EXCEPTION WHEN check_violation THEN NULL; END $$;
        INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id)
          VALUES ('00000000-0000-0000-0000-000000000023','GROUP','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000024');
        DO $$ BEGIN
          INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id)
            VALUES ('00000000-0000-0000-0000-000000000025','GROUP','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000024');
          RAISE EXCEPTION 'duplicate GROUP create accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id)
          VALUES ('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000021');
        DO $$ BEGIN
          INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id)
            VALUES ('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000021');
          RAISE EXCEPTION 'duplicate friendship accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        DO $$ BEGIN
          INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id)
            VALUES ('00000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000021');
          RAISE EXCEPTION 'reverse friendship accepted';
        EXCEPTION WHEN check_violation THEN NULL; END $$;
        INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
          VALUES ('00000000-0000-0000-0000-000000000031','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000041',1,'TEXT','hello');
        DO $$ BEGIN
          INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
            VALUES ('00000000-0000-0000-0000-000000000032','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000041',2,'TEXT','retry');
          RAISE EXCEPTION 'duplicate request accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        DO $$ BEGIN
          INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
            VALUES ('00000000-0000-0000-0000-000000000032','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000042',1,'TEXT','other');
          RAISE EXCEPTION 'duplicate seq accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,message_id,payload)
          VALUES ('00000000-0000-0000-0000-000000000051','Message','00000000-0000-0000-0000-000000000031','message.created','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000031','{}');
        DO $$ BEGIN
          INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,message_id,payload)
            VALUES ('00000000-0000-0000-0000-000000000052','Message','00000000-0000-0000-0000-000000000031','message.created','00000000-0000-0000-0000-000000000021','00000000-0000-0000-0000-000000000031','{}');
          RAISE EXCEPTION 'duplicate outbox event accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        INSERT INTO plugin_artifacts(plugin_id,version,package_hash,backend_hash,renderer_hash,manifest,status)
          VALUES ('echo','1','p','b','r','{}','VERIFIED');
        DO $$ BEGIN
          INSERT INTO plugin_artifacts(plugin_id,version,package_hash,backend_hash,renderer_hash,manifest,status)
            VALUES ('echo','1','changed','b','r','{}','VERIFIED');
          RAISE EXCEPTION 'duplicate artifact identity accepted';
        EXCEPTION WHEN unique_violation THEN NULL; END $$;
        DO $$ BEGIN
          UPDATE plugin_artifacts SET renderer_hash='changed' WHERE plugin_id='echo';
          RAISE EXCEPTION 'mutable artifact accepted';
        EXCEPTION WHEN raise_exception THEN
          IF SQLERRM = 'mutable artifact accepted' THEN RAISE; END IF;
        END $$;
        DO $$ BEGIN
          DELETE FROM plugin_artifacts WHERE plugin_id='echo';
          RAISE EXCEPTION 'artifact deletion accepted';
        EXCEPTION WHEN raise_exception THEN
          IF SQLERRM = 'artifact deletion accepted' THEN RAISE; END IF;
        END $$;
        """
        self.psql(sql)
        self.migrate("down", "--allow-data-loss")  #0002 preserves old product rows
        self.assertEqual(self.psql("SELECT count(*) FROM messages;"), "1")
        self.migrate("down", "--allow-data-loss")  #0001 retains historical rollback
        self.assertIn("pending", self.migrate("status"))
        self.assertEqual(self.psql("SELECT to_regclass('users') IS NULL AND to_regclass('messages') IS NULL;"), "t")
        self.migrate("up")
        self.migrate("down", "--allow-data-loss")
        self.migrate("down", "--allow-data-loss")


class OrderedMigrationStaticTests(unittest.TestCase):
    def test_ordered_plan_keeps_historical_checksum_and_one_locked_transaction(self):
        import importlib.util
        import hashlib
        spec = importlib.util.spec_from_file_location('group_migration_runner', RUNNER)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        self.assertEqual(runner.VERSIONS, ('0001_initial','0002_group_operations'))
        # This is the historical text checksum, including universal-newline
        # normalization; the tracked0001 files themselves are not rewritten.
        historical = 'e62294fdbdc5346c3a7b88b33777c50941a9b30df6bc6fa6e5f5b031bb11d098'
        self.assertEqual(hashlib.sha256(UP.read_text(encoding='utf8').encode('utf8')).hexdigest(),historical)
        self.assertEqual(runner.checksum('0001_initial'),historical)
        sql,versions = runner.transaction('up',{})
        self.assertEqual(versions,list(runner.VERSIONS))
        self.assertEqual(sql.count('BEGIN;'),1)
        self.assertEqual(sql.count('COMMIT;'),1)
        self.assertIn('pg_advisory_xact_lock(481233001)',sql)
        self.assertLess(sql.index('CREATE TABLE users'),sql.index('CREATE TABLE group_operation_receipts'))
        known = {version:runner.checksum(version) for version in runner.VERSIONS}
        down,versions = runner.transaction('down',known)
        self.assertEqual(versions,['0002_group_operations'])
        self.assertIn('DROP TABLE group_operation_receipts',down)
        self.assertNotIn('DROP TABLE users',down)
        with self.assertRaises(RuntimeError):runner.validate_ledger({'0002_group_operations':runner.checksum('0002_group_operations')})
        with self.assertRaises(RuntimeError):runner.validate_ledger({'0001_initial':'wrong'})


@unittest.skipUnless(os.environ.get('DB_TEST_ENABLE') == '1', 'set DB_TEST_ENABLE=1 with a disposable PostgreSQL database')
class GroupMigrationPostgreSQLTests(unittest.TestCase):
    def setUp(self):
        if not shutil.which('psql'):
            self.fail('DB_TEST_ENABLE=1 requires a real psql client')
        self.schema='group_db_test_'+uuid.uuid4().hex
        self.env=os.environ.copy()
        self.psql('CREATE SCHEMA '+self.schema+';',env=self.env)
        self.addCleanup(self.psql,'DROP SCHEMA '+self.schema+' CASCADE;',self.env.copy())
        self.env=self.env.copy()
        self.env['PGOPTIONS']='-c search_path='+self.schema

    def psql(self,sql,env=None,success=True):
        result=subprocess.run(['psql','-X','-v','ON_ERROR_STOP=1','-q','-A','-t'],input=sql,text=True,capture_output=True,env=env or self.env)
        if success:self.assertEqual(result.returncode,0,result.stderr)
        else:self.assertNotEqual(result.returncode,0,'SQL unexpectedly succeeded')
        return result.stdout.strip() if success else result.stderr

    def migrate(self,*args,success=True):
        result=subprocess.run([sys.executable,str(RUNNER),*args],text=True,capture_output=True,env=self.env)
        if success:self.assertEqual(result.returncode,0,result.stderr)
        else:self.assertNotEqual(result.returncode,0,'migration unexpectedly succeeded')
        return result.stdout if success else result.stderr

    def seed_0001(self):
        import hashlib
        text=UP.read_text(encoding='utf8')
        digest=hashlib.sha256(text.encode('utf8')).hexdigest()
        self.psql(text+f"\nCREATE TABLE schema_migrations(version text PRIMARY KEY,checksum text NOT NULL,applied_at timestamptz NOT NULL DEFAULT now()); INSERT INTO schema_migrations VALUES('0001_initial','{digest}','2001-01-01T00:00:00Z');")
        self.psql("""
        INSERT INTO users(user_id,username,display_name,password_hash) VALUES
          ('10000000-0000-4000-8000-000000000001','alice','Alice','hashed'),
          ('10000000-0000-4000-8000-000000000002','bob','Bob','hashed'),
          ('10000000-0000-4000-8000-000000000003','carol','Carol','hashed');
        INSERT INTO conversations(conversation_id,kind,created_by,direct_user_low_id,direct_user_high_id)
          VALUES('30000000-0000-4000-8000-000000000001','DIRECT','10000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000002');
        INSERT INTO conversation_members(conversation_id,user_id,role) VALUES
          ('30000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000001','OWNER'),
          ('30000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000002','MEMBER');
        INSERT INTO friendships(user_low_id,user_high_id,direct_conversation_id)
          VALUES('10000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000002','30000000-0000-4000-8000-000000000001');
        INSERT INTO messages(server_message_id,conversation_id,sender_id,request_id,seq,kind,text_body)
          VALUES('50000000-0000-4000-8000-000000000001','30000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000001','40000000-0000-4000-8000-000000000001',1,'TEXT','old fixture');
        INSERT INTO outbox_events(event_id,aggregate_type,aggregate_id,event_type,conversation_id,message_id,payload)
          VALUES('60000000-0000-4000-8000-000000000001','Message','50000000-0000-4000-8000-000000000001','message.created','30000000-0000-4000-8000-000000000001','50000000-0000-4000-8000-000000000001','{}');
        """)
        return digest

    def group(self):
        self.psql("""INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id)
          VALUES('30000000-0000-4000-8000-000000000002','GROUP','10000000-0000-4000-8000-000000000001','40000000-0000-4000-8000-000000000002');""")

    @staticmethod
    def receipt(operation='CREATE',request='40000000-0000-4000-8000-000000000002',targets=None,added=None,conversation='30000000-0000-4000-8000-000000000002'):
        targets=targets or "ARRAY['10000000-0000-4000-8000-000000000002']::uuid[]"
        added=added or "ARRAY['10000000-0000-4000-8000-000000000001','10000000-0000-4000-8000-000000000002']::uuid[]"
        return f"INSERT INTO group_operation_receipts(actor_id,operation,request_id,conversation_id,target_user_ids,added_member_user_ids) VALUES('10000000-0000-4000-8000-000000000001','{operation}','{request}','{conversation}',{targets},{added});"

    def test_empty_database_to_0002_status_repeat_and_staged_rollback(self):
        self.assertEqual(self.migrate('status').count('pending'),2)
        self.migrate('up')
        self.assertEqual(self.migrate('status').count('applied'),2)
        self.assertIn('already applied',self.migrate('up'))
        self.assertEqual(self.psql('SELECT count(*) FROM schema_migrations;'),'2')
        self.migrate('down','--allow-data-loss')
        self.assertEqual(self.psql("SELECT to_regclass('users') IS NOT NULL AND to_regclass('group_operation_receipts') IS NULL;"),'t')
        self.assertIn('0002_group_operations: pending',self.migrate('status'))
        self.migrate('up')
        self.migrate('down','--allow-data-loss')
        self.migrate('down','--allow-data-loss')
        self.assertEqual(self.psql("SELECT to_regclass('users') IS NULL;"),'t')
        self.assertIn('already rolled back',self.migrate('down','--allow-data-loss'))

    def test_upgrade_preserves_0001_rows_checksum_and_ledger_timestamp(self):
        digest=self.seed_0001()
        before=self.psql("SELECT checksum,applied_at FROM schema_migrations WHERE version='0001_initial';")
        self.migrate('up')
        self.assertEqual(self.psql("SELECT checksum,applied_at FROM schema_migrations WHERE version='0001_initial';"),before)
        self.assertIn(digest,before)
        self.assertEqual(self.psql('SELECT count(*) FROM users;'),'3')
        self.assertEqual(self.psql("SELECT text_body FROM messages;"),'old fixture')
        self.assertEqual(self.psql('SELECT count(*) FROM friendships;'),'1')
        self.assertEqual(self.psql('SELECT count(*) FROM conversation_members;'),'2')
        self.assertEqual(self.psql('SELECT count(*) FROM outbox_events;'),'1')
        self.migrate('down','--allow-data-loss')
        self.assertEqual(self.psql("SELECT text_body FROM messages;"),'old fixture')
        self.migrate('up')

    def test_checksums_and_unknown_or_gapped_ledger_fail_closed(self):
        digest=self.seed_0001()
        self.psql("UPDATE schema_migrations SET checksum='wrong';")
        self.assertIn('checksum',self.migrate('up',success=False))
        self.assertIn('checksum',self.migrate('status',success=False))
        self.assertIn('checksum',self.migrate('down','--allow-data-loss',success=False))
        self.assertEqual(self.psql("SELECT to_regclass('group_operation_receipts') IS NULL;"),'t')
        self.psql(f"UPDATE schema_migrations SET checksum='{digest}'; INSERT INTO schema_migrations(version,checksum) VALUES('9999_unknown','wrong');")
        self.assertIn('known ordered prefix',self.migrate('up',success=False))


    def test_single_physical_ledger_record_cannot_alias_canonical_rows(self):
        import hashlib
        digest1 = self.seed_0001()
        digest2 = hashlib.sha256((UP.parent / '0002_group_operations.up.sql').read_text(encoding='utf8').encode('utf8')).hexdigest()
        cases = (
            ('version', '0001_initial\t' + digest1 + '\n0002_group_operations', digest2),
            ('checksum', '0001_initial', digest1 + '\n0002_group_operations\t' + digest2),
        )
        for field, version, digest in cases:
            self.psql(f"UPDATE schema_migrations SET version='{version}',checksum='{digest}';")
            before = self.psql('SELECT json_agg(json_build_array(version,checksum,applied_at) ORDER BY version) FROM schema_migrations;')
            self.assertEqual(self.psql('SELECT count(*) FROM schema_migrations;'), '1')
            for arguments in (('status',), ('up',), ('down', '--allow-data-loss')):
                with self.subTest(field=field, arguments=arguments):
                    self.migrate(*arguments, success=False)
                    self.assertEqual(self.psql('SELECT json_agg(json_build_array(version,checksum,applied_at) ORDER BY version) FROM schema_migrations;'), before)
                    self.assertEqual(self.psql("SELECT to_regclass('group_operation_receipts') IS NULL;"), 't')
                    self.assertEqual(self.psql('SELECT text_body FROM messages;'), 'old fixture')

    def test_failure_in_0002_rolls_back_whole_pending_batch(self):
        self.psql('CREATE TABLE group_operation_receipts(preexisting int);')
        self.assertIn('already exists',self.migrate('up',success=False))
        self.assertEqual(self.psql("SELECT to_regclass('users') IS NULL AND to_regclass('schema_migrations') IS NULL AND to_regprocedure('group_operation_ids_canonical(uuid[])') IS NULL;"),'t')
        self.assertEqual(self.psql('SELECT count(*) FROM group_operation_receipts;'),'0')

    def test_receipts_keep_original_result_and_enforce_identity_and_targets(self):
        self.seed_0001();self.migrate('up');self.group()
        self.psql(self.receipt())
        original=self.psql('SELECT target_user_ids,added_member_user_ids,created_at FROM group_operation_receipts;')
        self.psql("INSERT INTO conversation_members(conversation_id,user_id,role) VALUES('30000000-0000-4000-8000-000000000002','10000000-0000-4000-8000-000000000003','MEMBER');")
        self.assertEqual(self.psql('SELECT target_user_ids,added_member_user_ids,created_at FROM group_operation_receipts;'),original)
        self.assertIn('duplicate key',self.psql(self.receipt(),success=False))
        self.psql(self.receipt('ADD',added="ARRAY[]::uuid[]"))
        self.assertEqual(self.psql('SELECT count(*) FROM group_operation_receipts;'),'2')
        self.psql("INSERT INTO conversations(conversation_id,kind,created_by,group_create_request_id) VALUES('30000000-0000-4000-8000-000000000003','GROUP','10000000-0000-4000-8000-000000000001','40000000-0000-4000-8000-000000000003');")
        self.assertIn('group_create_receipt_identity',self.psql(self.receipt(conversation='30000000-0000-4000-8000-000000000003'),success=False))
        self.psql(self.receipt('ADD',conversation='30000000-0000-4000-8000-000000000003',added="ARRAY[]::uuid[]"))

        for sql in [
            self.receipt('ADD',request='40000000-0000-4000-8000-000000000003',targets="ARRAY[]::uuid[]",added="ARRAY[]::uuid[]"),
            self.receipt('ADD',request='40000000-0000-4000-8000-000000000003',targets="ARRAY['10000000-0000-4000-8000-000000000002','10000000-0000-4000-8000-000000000002']::uuid[]",added="ARRAY[]::uuid[]"),
            self.receipt('ADD',request='40000000-0000-4000-8000-000000000003',targets="ARRAY['10000000-0000-4000-8000-000000000003','10000000-0000-4000-8000-000000000002']::uuid[]",added="ARRAY[]::uuid[]"),
            self.receipt('ADD',request='40000000-0000-4000-8000-000000000003',targets="ARRAY[NULL]::uuid[]",added="ARRAY[]::uuid[]"),
            self.receipt('ADD',request='40000000-0000-4000-8000-000000000003',targets="ARRAY['10000000-0000-4000-8000-000000000001']::uuid[]",added="ARRAY[]::uuid[]"),
            self.receipt('CREATE',request='40000000-0000-4000-8000-000000000003',added="ARRAY['10000000-0000-4000-8000-000000000002']::uuid[]"),
            self.receipt('ADD',request='40000000-0000-4000-8000-000000000003',added="ARRAY['10000000-0000-4000-8000-000000000003']::uuid[]"),
        ]:
            with self.subTest(sql=sql):self.assertIn('check constraint',self.psql(sql,success=False))
        self.assertEqual(self.psql('SELECT count(*) FROM group_operation_receipts;'),'3')

    def test_receipt_rollback_keeps_business_state_and_allows_reentry(self):
        self.seed_0001();self.migrate('up');self.group();self.psql(self.receipt())
        self.migrate('down','--allow-data-loss')
        self.assertEqual(self.psql("SELECT count(*) FROM conversations WHERE kind='GROUP';"),'1')
        self.assertEqual(self.psql("SELECT count(*) FROM messages;"),'1')
        self.assertEqual(self.psql('SELECT count(*) FROM schema_migrations;'),'1')
        self.migrate('up')
        self.assertEqual(self.psql('SELECT count(*) FROM group_operation_receipts;'),'0')

    @staticmethod
    def cleanup_process(process):
        if process.poll() is None:process.kill()
        process.wait(timeout=10)
        for stream in (process.stdin,process.stdout,process.stderr):
            if stream is not None and not stream.closed:stream.close()

    def test_lock_serializes_concurrent_runners_and_stale_state_fails_without_effects(self):
        import time
        self.psql('CREATE TABLE schema_migrations(version text PRIMARY KEY,checksum text NOT NULL,applied_at timestamptz NOT NULL DEFAULT now());')
        lock=subprocess.Popen(['psql','-X','-v','ON_ERROR_STOP=1','-q','-A','-t'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=self.env)
        self.addCleanup(self.cleanup_process,lock)
        lock.stdin.write("BEGIN; SELECT pg_advisory_xact_lock(481233001); SELECT 'lock-held';\n");lock.stdin.flush()
        while True:
            line=lock.stdout.readline()
            self.assertTrue(line,'lock holder terminated unexpectedly')
            if line.strip()=='lock-held':break
        runners=[subprocess.Popen([sys.executable,str(RUNNER),'up'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=self.env) for _ in range(2)]
        for process in runners:self.addCleanup(self.cleanup_process,process)
        deadline=time.monotonic()+10
        waiting=0
        while waiting<2 and time.monotonic()<deadline:
            waiting=int(self.psql("SELECT count(*) FROM pg_locks WHERE locktype='advisory' AND objid=481233001 AND NOT granted;"))
            if waiting<2:time.sleep(0.05)
        self.assertEqual(waiting,2,'both real runners must wait on the same transaction advisory lock')
        lock.stdin.write('COMMIT;\n');lock.stdin.close();lock.wait(timeout=10)
        results=[(process.communicate(timeout=20),process.returncode) for process in runners]
        self.assertEqual(sorted(code for _,code in results),[0,1])
        self.assertIn('migration state changed concurrently',''.join(stderr for (_,stderr),_ in results))
        self.assertEqual(self.psql('SELECT count(*) FROM schema_migrations;'),'2')
        self.assertIn('already applied',self.migrate('up'))


if __name__ == "__main__":
    unittest.main()
