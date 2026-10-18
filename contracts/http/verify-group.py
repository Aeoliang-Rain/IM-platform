"""Offline group schema/exchange oracle; this does not claim server acceptance."""
from __future__ import annotations

import json
from pathlib import Path
import re
import runpy
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / 'contracts/http/group.openapi.json'
ORACLE = runpy.run_path(str(ROOT / 'contracts/plugin-api/verify.py'))
Invalid = ORACLE['Invalid']
AUTH = ['AUTH_REQUIRED','AUTH_TOKEN_INVALID','AUTH_TOKEN_EXPIRED','AUTH_SESSION_REVOKED','AUTH_SESSION_EPOCH_STALE','AUTH_CLIENT_TYPE_MISMATCH']
BINDING = {
 'authentication':'authoritative-current-session-each-request-before-replay',
 'actor':'authorization-bearer-only-no-body-or-query-identity',
 'normalization':'canonical-lowercase-uuid-sort-distinct-targets-excluding-actor',
 'rawTargetLimit':100,'pageRowLimit':100,'bodyByteLimit':16384,
 'createKey':['actorId','CREATE','requestId'],'addKey':['actorId','conversationId','ADD','requestId'],
 'replay':'current-authorization-then-original-status-and-body',
 'conflict':'same-key-different-canonical-target-set-409-GROUP_REQUEST_CONFLICT',
 'authorization':'create-own-friends-add-current-group-member-own-friends-whole-batch',
 'alreadyMember':'still-check-friendship-no-new-member-or-change-event',
 'commit':'conversation-members-receipt-all-affected-user-sync-outbox-one-transaction-before-success',
 'unconfirmed':'retain-original-request-and-targets-never-assume-rollback-or-success',
 'snapshot':'current-effective-own-conversation-members-only-including-nonfriends',
 'order':['conversationId','member.user.userId'],
 'pagination':'strict-tuple-keyset-extra-row-hasMore-continue-to-terminal-no-total-cap',
 'consistency':'one-committed-page-not-global-multipage-snapshot',
 'refresh':'user-sync-invalidation-and-periodic-full-rescan-from-start-upsert-by-ids',
 'failure':'unknown-internal-failure-propagates-non-2xx-no-fabricated-canonical-error',
 'compatibility':'additive-old-direct-http-wss-ack-sync-unchanged',
 'missingOriginalResult':'existing-create-identity-without-verifiable-receipt-server-failure-no-guessed-replay-or-conflict'
}
PATHS = {'create':('/v1/groups','post','201'), 'add':('/v1/groups/{conversationId}/members','post','200'), 'list':('/v1/conversations','get','200')}


def require(condition, message):
    if not condition:
        raise Invalid(message)


def resolve_schema(node, document=CONTRACT, documents=None):
    """Adapt existing validator's local-only references to canonical external refs."""
    if isinstance(node, list):
        return [resolve_schema(value, document, documents) for value in node]
    if not isinstance(node, dict):
        return node
    if '$ref' in node:
        filename, _, fragment = node['$ref'].partition('#')
        target = (document.parent / filename).resolve() if filename else document
        require(target.is_relative_to(ROOT / 'contracts'), 'reference escapes contracts')
        value = documents if documents is not None and target == CONTRACT else json.loads(target.read_text(encoding='utf8'))
        for part in fragment.lstrip('/').split('/') if fragment else []:
            value = value[part.replace('~1','/').replace('~0','~')]
        resolved = resolve_schema(value, target, documents)
        siblings = {key: resolve_schema(value, document, documents) for key,value in node.items() if key != '$ref'}
        return {'allOf':[resolved,siblings]} if siblings else resolved
    return {key:resolve_schema(value, document, documents) for key,value in node.items()}


def without_patterns(schema):
    if isinstance(schema, list):
        return [without_patterns(value) for value in schema]
    if not isinstance(schema, dict):
        return schema
    if 'pattern' in schema:
        re.compile(schema['pattern'])
    return {key:without_patterns(value) for key,value in schema.items() if key != 'pattern'}


def check_patterns(value, schema):
    # Existing PublicUser/Username adds one regex keyword to the existing
    # standard-library validator. Retain its canonical pattern verbatim.
    if 'pattern' in schema and isinstance(value, str):
        require(re.search(schema['pattern'],value) is not None, 'canonical string pattern')
    for branch in schema.get('allOf',[]):
        check_patterns(value,branch)
    if 'oneOf' in schema:
        matches = 0
        for branch in schema['oneOf']:
            try:
                ORACLE['validate'](value,without_patterns(branch),{})
                check_patterns(value,branch)
                matches += 1
            except Invalid:
                pass  # A rejected alternative is not an operation failure.
        require(matches == 1, 'exactly one schema alternative including pattern')
    if isinstance(value, dict):
        for name, child in schema.get('properties',{}).items():
            if name in value:
                check_patterns(value[name],child)
    if isinstance(value, list) and 'items' in schema:
        for item in value:
            check_patterns(item,schema['items'])


def validate(value, schema, document=None):
    expanded = resolve_schema(schema, documents=document)
    base = without_patterns(expanded)
    ORACLE['lint'](base, {})
    ORACLE['validate'](value, base, {})
    check_patterns(value,expanded)


def structural_lint(document):
    node = shutil.which('node')
    require(bool(node), 'Node required for existing official OpenAPI3.1 structural lint')
    result = subprocess.run([node,str(ROOT/'contracts/http/check-openapi-3.1.js')], input=json.dumps(document).encode(),capture_output=True)
    require(result.returncode == 0,result.stderr.decode(errors='replace'))


def check_document(document):
    structural_lint(document)
    require(document['openapi'] == '3.1.0','OpenAPI3.1')
    require(document['servers'] == [{'url':'https://api.example.invalid'}],'HTTPS only')
    require(document['security'] == [{'bearerAuth':[]}],'Bearer default')
    require(document['x-group-binding'] == BINDING,'frozen group semantic binding')
    require(set(document['paths']) == {entry[0] for entry in PATHS.values()},'exact approved group routes')
    require(document['components']['securitySchemes'] == {'bearerAuth':{'$ref':'./auth-user-friend.openapi.json#/components/securitySchemes/bearerAuth'}},'reuse Bearer authority')
    require(set(document['components']['schemas']) == {'GroupRequest','GroupResult','Member','ConversationMemberView','Continuation','ConversationPage'},'bounded group schemas')
    catalog = json.loads((ROOT/'contracts/errors/http-errors.schema.json').read_text(encoding='utf8'))['$defs']['ErrorCode']['enum']
    for operation,(path,verb,success) in PATHS.items():
        require(set(document['paths'][path]) == {verb},'exact method')
        op = document['paths'][path][verb]
        require(op['security'] == [{'bearerAuth':[]}],'each operation authenticated')
        expected = {'400':['VALIDATION_FAILED'],'401':AUTH}
        require('content' not in op['responses']['default'] and 'x-error-codes' not in op['responses']['default'], 'unexpected failures never invent a canonical body/code')
        if operation != 'list':
            path_parameters = [{'name':'conversationId','in':'path','required':True,'schema':{'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'}}] if operation == 'add' else None
            require(op.get('parameters') == path_parameters, 'only approved mutation path parameter; no credential/query substitute')
            expected.update({'403':['AUTHORIZATION_DENIED'],'409':['GROUP_REQUEST_CONFLICT']})
            require(op['requestBody'] == {'required':True,'content':{'application/json':{'schema':{'$ref':'#/components/schemas/GroupRequest'}}}},'exact mutation body')
        else:
            require('requestBody' not in op,'GET has no body')
            require(op['parameters'][1]['schema'] == {'type':'integer','minimum':1,'maximum':100,'default':100},'bounded GET limit schema')
            require(all(p['schema'] == {'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'} for p in op['parameters'] if p['name'] != 'limit'),'reuse GET identifier authority')
            require([(p['name'],p['in'],p['required']) for p in op['parameters']] == [('requestId','query',True),('limit','query',False),('afterConversationId','query',False),('afterMemberUserId','query',False)],'exact GET parameters')
        require(set(op['responses']) == {success,'default'}|set(expected),'status set')
        for status,res in op['responses'].items():
            require(res['headers']['Cache-Control']['schema'] == {'type':'string','const':'no-store'},'no-store')
            if status in expected:
                require(res['x-error-codes'] == expected[status] and set(expected[status]) <= set(catalog),'status/error catalogue')
                require(res['content']['application/json']['schema'] == {'$ref':'../errors/http-errors.schema.json#/$defs/ErrorResponse'},'existing error shape')
    schemas = document['components']['schemas']
    require(schemas['Member']['properties']['user'] == {'$ref':'./auth-user-friend.openapi.json#/components/schemas/PublicUser'}, 'reuse minimal PublicUser authority')
    require(schemas['ConversationPage']['properties']['items']['maxItems'] == 100, 'actual row schema cap')
    body = document['components']['schemas']['GroupRequest']
    require(body['additionalProperties'] is False and body['required'] == ['requestId','memberUserIds'],'closed mutation body')
    require(body['properties']['memberUserIds'] == {'type':'array','minItems':1,'maxItems':100,'items':{'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'}},'bounded raw targets; duplicates normalized')
    for schema in document['components']['schemas'].values():
        ORACLE['lint'](without_patterns(resolve_schema(schema, documents=document)),{})


def operation_key(operation, actor, request):
    return (actor,'CREATE',request['body']['requestId']) if operation == 'create' else (actor,request['conversationId'],'ADD',request['body']['requestId'])


def request_failure(operation, request, context, document):
    """Only catalogued semantic rejections; unknown/internal failures are not mapped."""
    if request.get('unknownQuery') or request.get('bodyBytes',0) > BINDING['bodyByteLimit']:
        return 400,'VALIDATION_FAILED'
    if context.get('authError'):
        require(context['authError'] in AUTH,'known auth fixture cause')
        return 401,context['authError']
    validate(context['actorId'],{'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'})
    try:
        if operation == 'list':
            query = request.get('query',{})
            require(isinstance(query,dict),'query object')
            require(set(query) <= {'requestId','limit','afterConversationId','afterMemberUserId'},'query keys')
            require('requestId' in query,'query requestId required')
            validate(query['requestId'],{'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'})
            validate(query.get('limit',100),{'type':'integer','minimum':1,'maximum':100})
            require(('afterConversationId' in query) == ('afterMemberUserId' in query),'paired keyset')
            for name in ('afterConversationId','afterMemberUserId'):
                if name in query: validate(query[name],{'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'})
            require('body' not in request,'GET no body')
            return None
        validate(request.get('body'),document['components']['schemas']['GroupRequest'],document)
        if operation == 'add': validate(request.get('conversationId'),{'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'})
        targets = sorted(set(request['body']['memberUserIds']))
        require(context['actorId'] not in targets,'actor excluded')
    except Invalid:
        return 400,'VALIDATION_FAILED'
    if operation == 'add' and (context.get('kind') != 'GROUP' or context['actorId'] not in context.get('activeMemberIds',[])):
        return 403,'AUTHORIZATION_DENIED'
    if not set(targets) <= set(context.get('friendUserIds',[])):
        return 403,'AUTHORIZATION_DENIED'
    receipt = context.get('priorReceipt')
    if receipt and receipt['key'] == list(operation_key(operation,context['actorId'],request)) and receipt['targets'] != targets:
        return 409,'GROUP_REQUEST_CONFLICT'
    return None


def row_key(item):
    return item['conversationId'],item['member']['user']['userId']


def check_exchange(case, document=None):
    document = document or json.loads(CONTRACT.read_text(encoding='utf8'))
    operation,request,context = case['operation'],case['request'],case['context']
    path,verb,success = PATHS[operation]
    responses = document['paths'][path][verb]['responses']
    status = str(case['status'])
    failure = request_failure(operation,request,context,document)
    if context.get('originalResultUnavailable') and failure is None:
        require(operation == 'create' and context.get('existingCreateIdentity'), 'missing-result fixture has a durable existing identity')
        require(type(case['status']) is int and 500 <= case['status'] <= 599, 'missing original result fails as a server operation')
        require('response' not in case, 'never manufacture a canonical response or replay')
        require(case['observedFailure'] == {'cause':'persisted-original-group-result-missing','newEffects':0,'retainOriginalRequest':True}, 'real failure cause and zero new effects')
        return
    require(status in responses and status != 'default','declared response status')
    body = case['response']
    validate(body,responses[status]['content']['application/json']['schema'],document)
    validate(body['requestId'],{'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'})
    supplied = request.get('query',{}).get('requestId') if operation == 'list' else request.get('body',{}).get('requestId')
    if isinstance(supplied,str):
        try:
            validate(supplied,{'$ref':'./auth-user-friend.openapi.json#/components/schemas/Id'})
        except Invalid:
            pass  # An uncorrelatable request uses a new server UUID.
        else:
            require(body['requestId'] == supplied,'requestId correlation')
    if failure:
        require((case['status'],body.get('error',{}).get('code')) == failure,'authorization/validation/conflict precedence')
        require(body['error']['code'] in responses[status]['x-error-codes'],'error status/code')
        return
    require(status == success,'authorized well-formed request succeeds')
    if operation != 'list':
        targets = sorted(set(request['body']['memberUserIds']))
        receipt = context.get('priorReceipt')
        if receipt and receipt['key'] == list(operation_key(operation,context['actorId'],request)):
            require(case['status'] == receipt['status'] and body == receipt['response'],'replay original committed result')
        else:
            added = sorted({context['actorId'],*targets}) if operation == 'create' else sorted(set(targets)-set(context['activeMemberIds']))
            require(body['addedMemberUserIds'] == added,'only original actual members added')
        if operation == 'add': require(body['conversationId'] == request['conversationId'],'path/result conversation association')
        return
    query,items = request['query'],body['items']
    require(len(items) <= query.get('limit',100),'requested row cap')
    keys = [row_key(item) for item in items]
    require(keys == sorted(set(keys)),'strict unique tuple row order')
    previous = (query.get('afterConversationId',''),query.get('afterMemberUserId',''))
    require(all(key > previous for key in keys),'exclusive keyset progress')
    require(all(item['conversationId'] in context['ownConversationIds'] for item in items),'own current conversations only')
    require(all(list(key) in context['activeRows'] for key in keys),'effective members only')
    metadata = {}
    for item in items:
        conv = item['conversationId']
        current = {key:value for key,value in item.items() if key != 'member'}
        if conv in metadata: require(metadata[conv] == current,'within-page conversation metadata')
        metadata[conv] = current
    eligible = sorted(tuple(row) for row in context['activeRows']
                      if row[0] in context['ownConversationIds'] and tuple(row) > previous)
    require(keys == eligible[:len(keys)],'complete ordered eligible page prefix')
    require(bool(keys) or not eligible,'empty page only when no eligible rows remain')
    has_more = len(eligible) > len(keys)
    require(context['additionalRowExists'] == has_more,'fixture lookahead matches eligible rows')
    require(body['hasMore'] == has_more,'hasMore iff lookahead committed row')
    expected = dict(afterConversationId=keys[-1][0],afterMemberUserId=keys[-1][1]) if body['hasMore'] and keys else dict(afterConversationId='',afterMemberUserId='')
    require(not body['hasMore'] or bool(items),'hasMore requires nonempty progress')
    require(body['next'] == expected,'last-row continuation or terminal empty tuple')


def verify_fixtures(document):
    fixtures = json.loads((ROOT/'contracts/fixtures/group/exchanges.json').read_text(encoding='utf8'))
    ids = set()
    for kind in ('valid','invalid'):
        require(bool(fixtures[kind]),'positive and negative fixtures required')
        for case in fixtures[kind]:
            require(case['id'] not in ids,'unique fixture identity')
            ids.add(case['id'])
            if kind == 'valid':
                check_exchange(case,document)
            else:
                try:
                    check_exchange(case,document)
                except Invalid:
                    continue
                raise Invalid('negative exchange accepted: '+case['id'])
    require({'create-a-b','member-b-adds-nonfriend-c','create-original-replay-after-add','add-original-replay-after-later-add','existing-member-no-change','same-key-different-targets','revoked-replay','whole-batch-nonfriend','direct-denied','nonmember-denied','forged-actor-rejected','self-rejected','snapshot-nonfriend','snapshot-split-page','snapshot-terminal-empty','old-group-original-result-missing','new-group-original-result-missing'} <= ids,'mandatory exchange coverage')
    return len(fixtures['valid']),len(fixtures['invalid'])


def main():
    document = json.loads(CONTRACT.read_text(encoding='utf8'))
    check_document(document)
    positive,negative = verify_fixtures(document)
    print(f'PASS: official OpenAPI3.1/schema/exchange fixtures positive={positive} negative={negative}; offline authority only, server/runtime acceptance pending')


if __name__ == '__main__':
    main()
