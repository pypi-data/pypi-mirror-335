from enum import IntEnum


class HttpCode(IntEnum):
    # Namespace of Hypertext Transfer Protocol (HTTP) response status codes
    # Source: http://www.restapitutorial.com/httpstatuscodes.html

    # - This list contains all standard codes and some extensions.
    # - A 'POPULAR' comment tag is added to those codes that are particularly
    #   widespread in the world of REST APIs.
    # - A help section is provided for the popular codes.

    # Informational
    # =========================================================
    # Request received, continuing process.
    # This class of status code indicates a provisional response, consisting
    # only of the Status-Line and optional headers, and is terminated by an
    # empty line. Since HTTP/1.0 did not define any 1xx status codes, servers
    # must not[note 1] send a 1xx response to an HTTP/1.0 client except under
    # experimental conditions.
    Continue = 100
    SwitchingProtocols = 101
    Processing = 102

    # Success
    # =========================================================
    # This class of status codes indicates the action requested by the client
    # was received, understood, accepted and processed successfully.
    """
    The request has succeeded. The information returned with the 
    response is dependent on the method used in the request, for 
    example:
    - GET an entity corresponding to the requested resource is sent  in
      the response;
    - HEAD the entity-header fields corresponding to the requested 
      resource are sent in the response without any message-body;
    - POST an entity describing or containing the result of the action;
    - TRACE an entity containing the request message as received by the 
      end server.
    """
    OK = 200
    """
    The request has been fulfilled and resulted in a new resource being 
    created. The newly created resource can be referenced by the URI(s)
    returned in the entity of the response, with the most specific URI 
    for the resource given by a Location header field. The response 
    SHOULD include an entity containing a list of resource 
    characteristics and location(s) from which the user or user agent 
    can choose the one most appropriate. The entity format is specified 
    by the media type given in the Content-Type header field. The 
    origin server MUST create the resource before returning the 201 
    status code. If the action cannot be carried out immediately, the 
    server SHOULD respond with 202 (Accepted) response instead.
    """
    Created = 201
    """
    The request has been accepted for processing, but the processing 
    has not been completed. The request might or might not eventually 
    be acted upon, as it might be disallowed when processing actually 
    takes place. There is no facility for re-sending a status code from 
    an asynchronous operation such as this.
    The 202 response is intentionally non-committal. Its purpose is to 
    allow a server to accept a request for some other process 
    (perhaps a batch-oriented process that is only run once per day) 
    without requiring that the user agent's connection to the server 
    persist until the process is completed. The entity returned with 
    this response SHOULD include an indication of the request's current 
    status and either a pointer to a status monitor or some estimate of 
    when the user can expect the request to be fulfilled.
    """
    Accepted = 202
    NonAuthorativeInformation = 203
    """
    The server has fulfilled the request but does not need to return an 
    entity-body, and might want to return updated metainformation. The 
    response MAY include new or updated metainformation in the form of 
    entity-headers, which if present SHOULD be associated with the 
    requested variant.
    If the client is a user agent, it SHOULD NOT change its document 
    view from that which caused the request to be sent. This response 
    is primarily intended to allow input for actions to take place 
    without causing a change to the user agent's active document view, 
    although any new or updated metainformation SHOULD be applied to 
    the document currently in the user agent's active view.
    The 204 response MUST NOT include a message-body, and thus is 
    always terminated by the first empty line after the header fields.
    """
    NoContent = 204
    ResetContent = 205
    PartialContent = 206
    MultiStatus = 207
    AlreadyReported = 208
    IMUsed = 226

    # Redirection
    # =========================================================
    # This class of status codes indicates the client must take additional
    # action to complete the request. Many of these status codes are used in
    # URL redirection.
    # A user agent may carry out the additional action with no user
    # interaction only if the method used in the second request is GET or
    # HEAD. A user agent should not automatically redirect a request more
    # than five times, since such redirections usually indicate an infinite
    # loop.
    MultipleChoices = 300
    MovedPermanently = 301
    Found = 302
    SeeOther = 303
    """
    If the client has performed a conditional GET request and access is 
    allowed, but the document has not been modified, the server SHOULD 
    respond with this status code. The 304 response MUST NOT contain a 
    message-body, and thus is always terminated by the first empty line 
    after the header fields.
    The response MUST include the following header fields:

    - Date, unless its omission is required by section 14.18.1

    If a clockless origin server obeys these rules, and proxies and 
    clients add their own Date to any response received without one 
    (as already specified by [RFC 2068], section 14.19), caches will 
    operate correctly.
    - ETag and/or Content-Location, if the header would have been sent 
      in a 200 response to the same request
    - Expires, Cache-Control, and/or Vary, if the field-value might 
      differ from that sent in any previous response for the same 
      variant

    If the conditional GET used a strong cache validator (see section 
    13.3.3), the response SHOULD NOT include other entity-headers. 
    Otherwise (i.e., the conditional GET used a weak validator), the 
    response MUST NOT include other entity-headers; this prevents 
    inconsistencies between cached entity-bodies and updated headers.
    If a 304 response indicates an entity not currently cached, then 
    the cache MUST disregard the response and repeat the request 
    without the conditional.
    If a cache uses a received 304 response to update a cache entry, 
    the cache MUST update the entry to reflect any new field values 
    given in the response.
    """
    NotModified = 304
    UseProxy = 305
    # (Unused) = 306
    TemporaryRedirect = 307
    PermanentRedirect = 308

    # ClientError
    # =========================================================
    # This class of status codes is intended for cases in which the client
    # seems to have erred. Except when responding to a HEAD request, the
    # server should include an entity containing an explanation of the error
    # situation, and whether it is a temporary or permanent condition. These
    # status codes are applicable to any request method. User agents should
    # display any included entity to the user.
    """
    The request could not be understood by the server due to malformed 
    syntax. The client SHOULD NOT repeat the request without 
    modifications.
    """
    BadRequest = 400
    """
    The request requires user authentication. The response MUST include 
    a WWW-Authenticate header field (section 14.47) containing a 
    challenge applicable to the requested resource. The client MAY 
    repeat the request with a suitable Authorization header field 
    (section 14.8). If the request already included Authorization 
    credentials, then the 401 response indicates that authorization has 
    been refused for those credentials. If the 401 response contains 
    the same challenge as the prior response, and the user agent has 
    already attempted authentication at least once, then the user 
    SHOULD be presented the entity that was given in the response, 
    since that entity might include relevant diagnostic information.
    """
    Unauthorized = 401
    PaymentRequired = 402
    """
    The server understood the request, but is refusing to fulfill it. 
    Authorization will not help and the request SHOULD NOT be repeated. 
    If the request method was not HEAD and the server wishes to make 
    public why the request has not been fulfilled, it SHOULD describe 
    the reason for the refusal in the entity. If the server does not 
    wish to make this information available to the client, the status 
    code 404 (Not Found) can be used instead.
    """
    Forbidden = 403
    """
    The server has not found anything matching the Request-URI. No 
    indication is given of whether the condition is temporary or 
    permanent. The 410 (Gone) status code SHOULD be used if the server 
    knows, through some internally configurable mechanism, that an old 
    resource is permanently unavailable and has no forwarding address. 
    This status code is commonly used when the server does not wish to 
    reveal exactly why the request has been refused, or when no other 
    response is applicable.
    """
    NotFound = 404
    MethodNotAllowed = 405
    NotAcceptable = 406
    ProxyAuthenticationRequired = 407
    RequestTimeout = 408
    """
    The request could not be completed due to a conflict with the 
    current state of the resource. This code is only allowed in 
    situations where it is expected that the user might be able to 
    resolve the conflict and resubmit the request. The response body 
    SHOULD include enough information for the user to recognize the 
    source of the conflict. Ideally, the response entity would include 
    enough information for the user or user agent to fix the problem; 
    however, that might not be possible and is not required.
    Conflicts are most likely to occur in response to a PUT request. 
    For example, if versioning were being used and the entity being PUT 
    included changes to a resource which conflict with those made by an 
    earlier (third-party) request, the server might use the 409 
    response to indicate that it can't complete the request. In this 
    case, the response entity would likely contain a list of the 
    differences between the two versions in a format defined by the 
    response Content-Type.
    """
    Conflict = 409
    Gone = 410
    LengthRequired = 411
    PreconditionFailed = 412
    PayloadTooLarge = 413
    RequestURITooLong = 414
    UnsupportedMediaType = 415
    RequestedRangeNotSatisfiable = 416
    ExpectationFailed = 417
    ImATeapot = 418
    AuthenticationTimeout = 419
    MethodFailure = 420
    MisdirectedRequest = 421
    UnprocessableEntity = 422
    Locked = 423
    TooManyRequests = 429

    # ServerError
    # =========================================================
    # The server failed to fulfill an apparently valid request.
    # This class of status codes indicate cases in which the server is aware
    # that it has encountered an error or is otherwise incapable of
    # performing the request. Except when responding to a HEAD request, the
    # server should include an entity containing an explanation of the error
    # situation, and indicate whether it is a temporary or permanent
    # condition. Likewise, user agents should display any included entity to
    # the user. These response codes are applicable to any request method.
    """
    The server encountered an unexpected condition which prevented it 
    from fulfilling the request.
    """
    InternalServerError = 500
    NotImplemented = 501
    BadGateway = 502
    ServiceUnavailable = 503
    GatewayTimeout = 504
    HTTPVersionNotSupported = 505
    VariantAlsoNegotiates = 506
    InsufficientStorage = 507
    LoopDetected = 508
    BandwidthLimitExceeded = 509
    NotExtended = 510
    NetworkAuthenticationRequired = 511
    NetworkReadTimeoutError = 598
    NetworkConnectTimeoutError = 599
