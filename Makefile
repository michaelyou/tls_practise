#
# Build SSL certificates for our example.com
#

BITS=4096

www.pem: %.pem: %.crt %.key
	cat $*.crt $*.key > $*.pem

www.crt: %.crt: ca.cnf ca.key ca.crt %.csr
	openssl ca -batch -config ca.cnf -days 36500 \
        -keyfile ca.key -cert ca.crt \
        -in $*.csr -outdir . -out $*.crt

www.csr: %.csr: %.key %.cnf
	openssl req -new -key $*.key -config $*.cnf -out $*.csr

www.key:
	openssl genrsa -out $@ $(BITS)
