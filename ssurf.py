from multiprocessing import Process, Queue
from twisted.internet import reactor, endpoints, defer
from twisted.names import client, dns, error, server
from klein import Klein
import socket
import re


class DynamicResolver(object):
    """
    A resolver which returns an IP that was fed into the REST API.
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
        query the name
        """
        try:
             self._ip = self._ipqueue.get(block=False)
             print self._ip
        except Exception as e:
             print "nothing in the queue: {}".format(type(e))
             print "the IP is still: {}".format(self._ip)
        print "The query is: {} and the IP is: {}".format(query.name.name, self._ip)
        return defer.succeed(self._doDynamicResponse(query))


def webserver(pq):
    webapp = Klein()

    @webapp.route('/')
    def home(request):
        return 'Hello, World!'

    @webapp.route('/ip/<ip>')
    def getIP(request, ip):
        # We only need ipv4 dotted-quad. Quick regex check, then test the validity of the IP
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip):
            try:
                socket.inet_aton(ip)
                pq.put(ip)
                print "ip is: {}".format(ip)
                return "ip is: {}".format(ip)
            except socket.error:
                print "input is not an IP."
                return "This is an IP! Read the RFC 791: https://tools.ietf.org/html/rfc791"
        else:
            print "input is not an IP."
            return "This is not an IP! Read the RFC 791: https://tools.ietf.org/html/rfc791"

    webapp.run(host="0.0.0.0", port=8080)


def dnsserver(pq):
    dynresolver = DynamicResolver()
    dynresolver._ipqueue = pq
    factory = server.DNSServerFactory(
        clients=[dynresolver, client.Resolver(resolv='/etc/resolv.conf')]
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)
    reactor.listenUDP(10053, protocol, interface="0.0.0.0")
    reactor.listenTCP(10053, factory, interface="0.0.0.0")

    reactor.run()


if __name__ == "__main__":
    q = Queue()
    webproc = Process(target=webserver, args=[q])
    dnsproc = Process(target=dnsserver, args=[q])

    webproc.start()
    dnsproc.start()
