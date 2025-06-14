import packages.connectors as connectors

print("accessible thru",connectors.getPrivateIp())
llmss = connectors.llmServerSide()
proflss = connectors.profilesServerSide()

llmss.start()
proflss.start()