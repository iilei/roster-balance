from fastapi.testclient import TestClient

from roster_balance.main import app

client = TestClient(app)


def test_team_crud_is_exposed_in_openapi_and_http() -> None:
    schema = client.get('/openapi.json').json()
    assert '/teams' in schema['paths']
    assert '/teams/{team_id}' in schema['paths']
    assert '/teams/{team_id}/team-members' in schema['paths']
    assert '/teams/{team_id}/eligible-members' in schema['paths']
    assert 'put' not in schema['paths']['/teams/{team_id}/team-members']
    assert 'delete' in schema['paths']['/teams/{team_id}/team-members/{user_id}']

    created = client.post(
        '/teams',
        json={'name': 'Platform', 'description': 'Core services'},
    )
    assert created.status_code == 201
    team = created.json()
    assert team['name'] == 'Platform'

    fetched = client.get(f'/teams/{team["id"]}')
    assert fetched.status_code == 200
    assert fetched.json()['id'] == team['id']

    updated = client.patch(f'/teams/{team["id"]}', json={'active': False})
    assert updated.status_code == 200
    assert updated.json()['active'] is False

    cleared = client.patch(f'/teams/{team["id"]}', json={'description': None})
    assert cleared.status_code == 200
    assert cleared.json()['description'] is None

    deleted = client.delete(f'/teams/{team["id"]}')
    assert deleted.status_code == 204
    assert client.get(f'/teams/{team["id"]}').status_code == 404


def test_duplicate_team_names_are_rejected() -> None:
    first = client.post('/teams', json={'name': 'Unique team'})
    assert first.status_code == 201
    duplicate = client.post('/teams', json={'name': 'UNIQUE TEAM'})
    assert duplicate.status_code == 409


def test_teams_can_be_searched_by_name_or_description() -> None:
    client.post('/teams', json={'name': 'Search Platform'})
    client.post(
        '/teams',
        json={'name': 'Operations', 'description': 'Platform support'},
    )

    by_name = client.get('/teams', params={'q': 'SEARCH platform'})
    assert by_name.status_code == 200
    assert [team['name'] for team in by_name.json()] == ['Search Platform']

    by_description = client.get('/teams', params={'q': 'SUPPORT'})
    assert by_description.status_code == 200
    assert [team['name'] for team in by_description.json()] == ['Operations']

    assert client.get('/teams', params={'q': 'missing'}).json() == []
    assert client.get('/teams', params={'q': ''}).status_code == 422


def test_team_creator_is_added_as_owner() -> None:
    created = client.post('/teams', json={'name': 'Owned team'})
    assert created.status_code == 201

    owners = client.get(
        f'/teams/{created.json()["id"]}/team-members',
        params={'role': 'owner'},
    )
    assert owners.status_code == 200
    assert owners.json()[0]['user_id'] == 'local:dev'
    assert owners.json()[0]['role'] == 'owner'


def test_team_membership_does_not_make_a_member_roster_eligible() -> None:
    created = client.post('/teams', json={'name': 'Eligibility team'})
    team_id = created.json()['id']

    members = client.get(f'/teams/{team_id}/team-members')
    eligible = client.get(f'/teams/{team_id}/eligible-members')

    assert members.status_code == 200
    assert eligible.status_code == 200
    assert eligible.json() == []

    role = client.post(
        f'/teams/{team_id}/duty-roles',
        json={'slug': 'on-call', 'display_name': 'On-call'},
    )
    assert role.status_code == 201

    added = client.post(
        f'/teams/{team_id}/eligible-members/on-call',
        json={'member_id': 'local:dev'},
    )
    assert added.status_code == 201
    assert added.json()['member_id'] == 'local:dev'
    assert added.json()['duty_role'] == 'on-call'

    removed = client.delete(f'/teams/{team_id}/eligible-members/on-call/local:dev')
    assert removed.status_code == 204


def test_me_returns_the_local_user() -> None:
    response = client.get('/me')

    assert response.status_code == 200
    assert response.json()['principal'] == 'local:dev'
    assert response.json()['user']['id'] == 'local:dev'


def test_owner_can_submit_generic_team_invitation() -> None:
    schema = client.get('/openapi.json').json()
    assert '/teams/{team_id}/invitations' in schema['paths']
    assert '/invitations/{invitation_id}/accept' in schema['paths']

    created = client.post('/teams', json={'name': 'Invitation team'})
    invitation = client.post(
        f'/teams/{created.json()["id"]}/invitations',
        json={'email': 'Alice@Example.com'},
    )

    assert invitation.status_code == 202
    assert invitation.json() == {'status': 'accepted_for_delivery'}

    delivery = client.get('/dev/invitations/latest/delivery')
    assert delivery.status_code == 200
    assert delivery.json()['mailto_url'].startswith('mailto:alice@example.com?')
    assert '/invitations/' in delivery.json()['preview_url']
    assert 'token=' in delivery.json()['preview_url']
