import httpx,pytest
from statement_ledger.connectors.http import YouTubeClient,FactCheckClient,ArchiveClient,AAPBClient,SourceError

def test_youtube_token_and_fixed_host():
    def respond(req):
        assert req.url.host=="www.googleapis.com"
        assert req.url.params["pageToken"]=="next"
        assert req.url.params["type"]=="video"
        return httpx.Response(200,json={"items":[],"nextPageToken":"last"})
    with YouTubeClient("secret",transport=httpx.MockTransport(respond)) as c:
        page=c.search("Dana",cursor="next");assert page.next_cursor=="last"

def test_playlist_resolution():
    def respond(req):return httpx.Response(200,json={"items":[{"contentDetails":{"relatedPlaylists":{"uploads":"UUfixture"}}}]})
    with YouTubeClient("secret",transport=httpx.MockTransport(respond)) as c:assert c.uploads_playlist("UCfixture")=="UUfixture"

def test_google_claim_search():
    def respond(req):
        assert req.url.path.endswith("claims:search")
        assert req.url.params["query"]=="example"
        return httpx.Response(200,json={"claims":[]})
    with FactCheckClient("secret",transport=httpx.MockTransport(respond)) as c:assert c.search("example").next_cursor is None

@pytest.mark.parametrize("status",[301,302,401,403,404])
def test_errors_redact_credentials_and_body(status):
    with YouTubeClient("ULTRASECRET",transport=httpx.MockTransport(lambda r:httpx.Response(status,text="ULTRASECRET")),retries=0) as c:
        with pytest.raises(SourceError) as exc:c.search("x")
        assert "ULTRASECRET" not in str(exc.value)

def test_retry_budget():
    hits=[]
    def respond(req):hits.append(1);return httpx.Response(503)
    with YouTubeClient("secret",transport=httpx.MockTransport(respond),retries=2,sleeper=lambda _:None) as c:
        with pytest.raises(SourceError):c.search("x")
    assert len(hits)==3

def test_response_limit():
    with YouTubeClient("s",transport=httpx.MockTransport(lambda r:httpx.Response(200,content=b'x'*50)),max_bytes=10) as c:
        with pytest.raises(SourceError,match="bound"):c.search("x")

def test_archive_pagination():
    with ArchiveClient(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={"response":{"numFound":101,"docs":[]}}))) as c:
        assert c.search("x",page=1,rows=50).next_cursor=="2"
        assert c.search("x",page=3,rows=50).next_cursor is None
        with pytest.raises(ValueError):c.metadata("../../etc/passwd")

def test_aapb_pagination():
    with AAPBClient(transport=httpx.MockTransport(lambda r:httpx.Response(200,json={"response":{"numFound":101,"docs":[]}}))) as c:
        assert c.search("x",start=50,rows=50).next_cursor=="100"

@pytest.mark.parametrize("klass",[YouTubeClient,FactCheckClient])
def test_missing_credentials(klass):
    with pytest.raises(ValueError):klass("")
