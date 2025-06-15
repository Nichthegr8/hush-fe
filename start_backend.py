import packages.connectors as connectors

print("accessible thru",connectors.getPrivateIp())
llmss = connectors.llmServerSide()
proflss = connectors.profilesServerSide()
audescss = connectors.audioDescServerSide(llmss=llmss)

llmss.start()
proflss.start()
audescss.start()