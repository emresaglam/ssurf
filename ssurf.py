from multiprocessing import Process, Queue
from twisted.internet import reactor, endpoints, defer
from twisted.names import client, dns, error, server
from klein import Klein


class DynamicResolver(object):
    """
    A resolver which calculates the answers to certain queries based on the
    query type and name.
    """
    _ip = '192.168.0.1'
    _ipqueue = Queue()

    def _doDynamicResponse(self, query):
        """
        Calculate the response to a query.
        """
        name = query.name.name
        answer = dns.RRHeader(
            name=name,
            payload=dns.Record_A(address=b'%s' % (self._ip)))
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional

    def query(self, query, timeout=None):
        """
        Check if the query should be answered dynamically, otherwise dispatch to
        the fallback resolver.
        """
        try:
             self._ip = self._ipqueue.get(block=False)
             print self._ip
        except Exception as e:
             print "nothing in the queue: {}".format(type(e))
             print "the IP is still: {}".format(self._ip)
        print "The query is: {} and the IP is: {}".format(query, self._ip)
        return defer.succeed(self._doDynamicResponse(query))


def webserver(pq):
    webapp = Klein()

    @webapp.route('/')
    def home(request):
        return 'Hello, World!'

    @webapp.route('/ip/<ip>')
    def getIP(request, ip):
        pq.put(ip)
        print "ip is: {}".format(ip)
        return "ip is: {}".format(ip)

    webapp.run(host="localhost", port=8080)


def dnsserver(pq):
    dynresolver = DynamicResolver()
    dynresolver._ipqueue = pq
    factory = server.DNSServerFactory(
        clients=[dynresolver, client.Resolver(resolv='/etc/resolv.conf')]
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)
    reactor.listenUDP(10053, protocol)
    reactor.listenTCP(10053, factory)

    reactor.run()


if __name__ == "__main__":
    q = Queue()
    webproc = Process(target=webserver, args=[q])
    dnsproc = Process(target=dnsserver, args=[q])

    webproc.start()
    dnsproc.start()
