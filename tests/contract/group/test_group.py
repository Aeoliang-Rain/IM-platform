import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

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

    def test_skipped_eligible_rows_and_incomplete_terminal_pages_are_rejected(self):
        for name in ('snapshot-nonfriend','snapshot-split-page','snapshot-resume-terminal'):
            original=self.case(name)
            omitted=range(len(original['response']['items'])-1) if original['response']['hasMore'] else range(len(original['response']['items']))
            for index in omitted:
                with self.subTest(fixture=name,omitted=index):
                    case=copy.deepcopy(original)
                    del case['response']['items'][index]
                    if case['response']['hasMore'] and case['response']['items']:
                        last=v.row_key(case['response']['items'][-1])
                        case['response']['next']=dict(afterConversationId=last[0],afterMemberUserId=last[1])
                    with self.assertRaises(v.Invalid):v.check_exchange(case)
        case=self.case('snapshot-nonfriend');case['response']['items']=[]
        with self.assertRaises(v.Invalid):v.check_exchange(case)

    def test_lookahead_is_derived_even_when_context_and_response_agree(self):
        for name in ('snapshot-nonfriend','snapshot-split-page'):
            case=self.case(name);more=not case['response']['hasMore']
            case['context']['additionalRowExists']=more
            case['response']['hasMore']=more
            last=v.row_key(case['response']['items'][-1])
            case['response']['next']=dict(afterConversationId=last[0],afterMemberUserId=last[1]) if more else dict(afterConversationId='',afterMemberUserId='')
            with self.subTest(fixture=name),self.assertRaises(v.Invalid):v.check_exchange(case)

    def test_page_prefix_uses_full_tuple_order_and_own_conversation_filter(self):
        case=self.case('snapshot-split-page')
        first,second=case['response']['items']
        later=copy.deepcopy(first);later['conversationId']='30000000-0000-4000-8000-000000000002'
        outside=copy.deepcopy(first);outside['conversationId']='30000000-0000-4000-8000-000000000003'
        case['context']['ownConversationIds'].append(later['conversationId'])
        case['context']['activeRows']=[list(v.row_key(row)) for row in (outside,later,second,first)]
        case['request']['query'].update(afterConversationId=first['conversationId'],afterMemberUserId=first['member']['user']['userId'])
        case['response'].update(items=[second,later],hasMore=False,next=dict(afterConversationId='',afterMemberUserId=''))
        case['context']['additionalRowExists']=False
        v.check_exchange(case)
        for omitted in (0,1):
            incomplete=copy.deepcopy(case);del incomplete['response']['items'][omitted]
            with self.subTest(omitted=omitted),self.assertRaises(v.Invalid):v.check_exchange(incomplete)

    def test_short_ordered_prefix_with_truthful_lookahead_can_reach_terminal(self):
        for limit in (2,None):
            with self.subTest(limit=limit):
                first=self.case('snapshot-split-page');all_rows=self.case('snapshot-nonfriend')['response']['items']
                if limit is None:first['request']['query'].pop('limit')
                first['response']['items']=all_rows[:1]
                first['response']['next']=dict(afterConversationId=all_rows[0]['conversationId'],afterMemberUserId=all_rows[0]['member']['user']['userId'])
                v.check_exchange(first)
                last=copy.deepcopy(first)
                last['request']['query'].update(first['response']['next'])
                last['response'].update(items=all_rows[1:],hasMore=False,next=dict(afterConversationId='',afterMemberUserId=''))
                last['context']['additionalRowExists']=False
                v.check_exchange(last)
                self.assertEqual(first['response']['items']+last['response']['items'],all_rows)

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


    def test_checker_internal_exits_cannot_pass_formal_negative_test(self):
        for code in (2,37,-9):
            with self.subTest(exit_code=code):
                process=v.subprocess.CompletedProcess([],code,stdout=b'checker-output-sentinel',stderr=b'checker-internal-sentinel')
                result=unittest.TestResult()
                with mock.patch.object(v.subprocess,'run',return_value=process) as checker:
                    GroupContractTests('test_formal_openapi_structure_negative_controls').run(result)
                self.assertFalse(result.wasSuccessful())
                self.assertEqual((len(result.failures),len(result.errors)),(0,1))
                self.assertEqual(checker.call_count,1)
                diagnostic=result.errors[0][1]
                for expected in ('RuntimeError',f'exit {code}','checker-output-sentinel','checker-internal-sentinel'):
                    self.assertIn(expected,diagnostic)

    def test_structural_checker_missing_node_and_launch_defects_propagate(self):
        with mock.patch.object(v.shutil,'which',return_value=None),mock.patch.object(v.subprocess,'run') as checker:
            with self.assertRaisesRegex(RuntimeError,'Node required'):
                v.structural_lint(self.document)
            checker.assert_not_called()
        for fault in (FileNotFoundError('missing-node-executable'),OSError('launch-failed'),ValueError('internal-invocation-defect')):
            with self.subTest(fault=type(fault).__name__),mock.patch.object(v.subprocess,'run',side_effect=fault):
                with self.assertRaises(type(fault)) as observed:
                    v.structural_lint(self.document)
                self.assertIs(observed.exception,fault)

    def test_real_checker_success_and_schema_rejection_exit_codes(self):
        for valid in (True,False):
            candidate=copy.deepcopy(self.document)
            if not valid:candidate['info'].pop('title')
            with self.subTest(valid=valid):
                real_run=v.subprocess.run;children=[]
                def observe(*args,**kwargs):
                    child=real_run(*args,**kwargs);children.append(child);return child
                with mock.patch.object(v.subprocess,'run',side_effect=observe) as checker:
                    if valid:v.structural_lint(candidate)
                    else:
                        with self.assertRaises(v.Invalid):v.structural_lint(candidate)
                self.assertEqual(checker.call_count,1)
                child=children[0]
                self.assertEqual(child.returncode,0 if valid else 1)
                if not valid:self.assertTrue(child.stderr)


    def test_nonobject_requests_accept_canonical_errors_and_reject_bad_responses(self):
        for name,field in (('create-a-b','body'),('member-b-adds-nonfriend-c','body'),('snapshot-nonfriend','query')):
            for encoded in ('null','[]','true','42','"decoded scalar JSON"','{}'):
                with self.subTest(fixture=name,json=encoded):
                    original=self.case(name);case=copy.deepcopy(original)
                    case['request'][field]=json.loads(encoded)
                    case['status']=400
                    case['response']={'requestId':'40000000-0000-4000-8000-000000000099','error':{'code':'VALIDATION_FAILED','message':'Request validation failed.'}}
                    self.assertEqual(v.request_failure(case['operation'],case['request'],case['context'],self.document),(400,'VALIDATION_FAILED'))
                    v.check_exchange(case,self.document)
                    mutations=[
                        ('status',lambda c:c.__setitem__('status',401)),
                        ('code',lambda c:c['response']['error'].__setitem__('code','AUTH_REQUIRED')),
                        ('requestId',lambda c:c['response'].__setitem__('requestId','not-a-uuid')),
                        ('success',lambda c:c.update(status=original['status'],response=original['response'])),
                    ]
                    for label,mutate in mutations:
                        invalid=copy.deepcopy(case);mutate(invalid)
                        with self.subTest(mutation=label),self.assertRaises(v.Invalid):v.check_exchange(invalid,self.document)

    def test_malformed_objects_with_valid_request_ids_still_require_correlation(self):
        for name,field in (('create-a-b','body'),('member-b-adds-nonfriend-c','body'),('snapshot-nonfriend','query')):
            with self.subTest(fixture=name):
                case=self.case(name);request_id=case['request'][field]['requestId']
                case['request'][field]={'requestId':request_id,'limit':0} if field=='query' else {'requestId':request_id,'memberUserIds':[]}
                case['status']=400
                case['response']={'requestId':request_id,'error':{'code':'VALIDATION_FAILED','message':'Request validation failed.'}}
                v.check_exchange(case,self.document)
                case['response']['requestId']='40000000-0000-4000-8000-000000000099'
                with self.assertRaises(v.Invalid):v.check_exchange(case,self.document)


if __name__=='__main__':unittest.main()
