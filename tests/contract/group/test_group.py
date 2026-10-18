import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('group_contract', ROOT/'contracts/http/verify-group.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class GroupContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document=json.loads(v.CONTRACT.read_text(encoding='utf8'))
        cls.fixtures=json.loads((ROOT/'contracts/fixtures/group/exchanges.json').read_text(encoding='utf8'))

    def case(self,name):
        return copy.deepcopy(next(case for case in self.fixtures['valid'] if case['id']==name))

    def test_actual_official_openapi_lint_and_all_positive_negative_exchanges(self):
        v.check_document(self.document)
        positive,negative=v.verify_fixtures(self.document)
        self.assertGreaterEqual(positive,30)
        self.assertGreaterEqual(negative,20)

    def test_formal_openapi_structure_negative_controls(self):
        mutations=[
            lambda d:d['info'].pop('title'),
            lambda d:d.__setitem__('unknownRoot',1),
            lambda d:d['paths']['/v1/groups']['post']['responses'].__setitem__('201',42),
            lambda d:d['paths']['/v1/groups']['post'].__setitem__('unknownOperation',1),
            lambda d:d['paths']['/v1/conversations']['get']['parameters'][0].__setitem__('in','imaginary'),
        ]
        for mutate in mutations:
            candidate=copy.deepcopy(self.document);mutate(candidate)
            with self.assertRaises(v.Invalid):v.structural_lint(candidate)

    def test_contract_security_and_resource_negative_controls(self):
        mutations=[
            lambda d:d.__setitem__('security',[]),
            lambda d:d['servers'][0].__setitem__('url','http://api.example.invalid'),
            lambda d:d['paths']['/v1/groups']['post'].__setitem__('security',[]),
            lambda d:d['paths']['/v1/groups']['post']['requestBody'].__setitem__('required',False),
            lambda d:d['components']['schemas']['GroupRequest']['properties']['memberUserIds'].__setitem__('maxItems',100000),
            lambda d:d['x-group-binding'].__setitem__('replay','current-membership'),
            lambda d:d['x-group-binding'].__setitem__('pageRowLimit',100000),
            lambda d:d['x-group-binding'].__setitem__('pagination','fixed-total-100'),
            lambda d:d['paths']['/v1/groups/{conversationId}/members']['post']['responses']['403'].__setitem__('x-error-codes',['USER_NOT_FOUND']),
        ]
        for mutate in mutations:
            candidate=copy.deepcopy(self.document);mutate(candidate)
            with self.assertRaises(v.Invalid):v.check_document(candidate)

    def test_request_schema_positive_and_negative_vectors(self):
        schema=self.document['components']['schemas']['GroupRequest']
        body=self.case('create-a-b')['request']['body']
        v.validate(body,schema)
        v.validate(dict(body,memberUserIds=body['memberUserIds']*100),schema)
        for invalid in ({},dict(body,actorId=body['memberUserIds'][0]),dict(body,memberUserIds=[]),dict(body,memberUserIds=body['memberUserIds']*101),dict(body,memberUserIds=[True]),dict(body,requestId='wrong')):
            with self.subTest(invalid=invalid),self.assertRaises(v.Invalid):v.validate(invalid,schema)

    def test_original_receipt_is_not_reconstructed_after_later_membership(self):
        for name in ('create-original-replay-after-add','add-original-replay-after-later-add'):
            case=self.case(name);v.check_exchange(case)
            case['response']['addedMemberUserIds']=case['context']['activeMemberIds']
            with self.assertRaises(v.Invalid):v.check_exchange(case)

    def test_current_authorization_precedes_replay_and_conflict(self):
        for name in ('revoked-replay','replay-existing-target-still-needs-friend'):
            case=self.case(name);v.check_exchange(case)
            case['status']=201 if case['operation']=='create' else 200
            case['response']=case['context']['priorReceipt']['response']
            with self.assertRaises(v.Invalid):v.check_exchange(case)

    def test_idempotency_scopes_are_separate_and_orderless(self):
        case=self.case('target-order-and-duplicates');v.check_exchange(case)
        for name in ('different-actor-same-request','same-request-different-conversation','same-request-different-operation'):
            v.check_exchange(self.case(name))
        create=self.case('create-a-b');add=self.case('same-request-different-operation')
        self.assertNotEqual(v.operation_key('create',create['context']['actorId'],create['request']),v.operation_key('add',add['context']['actorId'],add['request']))

    def test_joined_rows_allow_complete_member_pagination_and_nonfriends(self):
        first=self.case('snapshot-split-page');last=self.case('snapshot-resume-terminal')
        v.check_exchange(first);v.check_exchange(last)
        rows=first['response']['items']+last['response']['items']
        self.assertEqual(len({v.row_key(row) for row in rows}),3)
        self.assertEqual(rows[-1]['member']['user']['displayName'],'Carol 非好友')
        self.assertEqual(rows[0]['member']['user']['displayName'],rows[1]['member']['user']['displayName'])
        self.assertNotEqual(rows[0]['member']['user']['userId'],rows[1]['member']['user']['userId'])

    def test_more_than_one_page_and_no_total_group_size_cap(self):
        template=self.case('snapshot-nonfriend');base=template['response']['items'][0]
        members=[]
        for index in range(1,238):
            row=copy.deepcopy(base)
            row['member']['user']['userId']=f'10000000-0000-4000-8000-{index:012d}'
            row['member']['user']['username']=f'user{index}'
            members.append(row)
        context=template['context'];context['activeRows']=[list(v.row_key(row)) for row in members]
        query={'requestId':template['response']['requestId'],'limit':100}
        received=[]
        for offset in (0,100,200):
            case=copy.deepcopy(template);items=members[offset:offset+100];more=offset+len(items)<len(members)
            case['request']['query']=copy.deepcopy(query);case['context']['additionalRowExists']=more
            case['response'].update(items=items,hasMore=more,next={'afterConversationId':items[-1]['conversationId'],'afterMemberUserId':items[-1]['member']['user']['userId']} if more else {'afterConversationId':'','afterMemberUserId':''})
            v.check_exchange(case);received.extend(items)
            if more:query.update(case['response']['next'])
        self.assertEqual(len(received),237)
        self.assertFalse(case['response']['hasMore'])

    def test_candidate_internal_references_validate_candidate_schemas(self):
        candidate=copy.deepcopy(self.document)
        candidate['components']['schemas']['GroupResult']['properties']['addedMemberUserIds']['items']={'type':'integer'}
        with self.assertRaises(v.Invalid):v.check_exchange(self.case('create-a-b'),candidate)

    def test_internal_fixture_errors_propagate_without_false_validation_failure(self):
        case=self.case('create-a-b');case['context'].pop('actorId')
        with self.assertRaises(KeyError):v.check_exchange(case)

    def test_runtime_transaction_vectors_are_declared_pending(self):
        fixtures=json.loads((ROOT/'contracts/fixtures/group/transaction-vectors.json').read_text(encoding='utf8'))
        self.assertEqual(fixtures['runtimeAcceptance'],'PENDING')
        names={case['id'] for case in fixtures['vectors']}
        self.assertTrue({'concurrent-create-same-key','concurrent-add-same-key','overlap-different-actor-request','write-failure-rollback','response-loss-before-commit','response-loss-after-commit','compatibility-old-client','concurrent-list-insert-before-cursor'} <= names)

    def test_existing_shared_step_executes_both_new_entrypoints_and_propagates_failure(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        step=workflow.split('- name: HTTP, WSS, Sync and Plugin contracts',1)[1].split('\n  compatibility:',1)[0]
        for command in ('python3 -B contracts/http/verify-group.py','python3 -B -m unittest discover -s tests/contract/group -p "test_*.py" -v'):
            self.assertIn(command+'\n          if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }',step)


if __name__=='__main__':unittest.main()
