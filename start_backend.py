import packages.connectors as connectors

print(f"Started servers on {connectors.listeners.getPrivateIp()}")

llmss = connectors.llmServerSide()
proflss = connectors.profilesServerSide()

llmss.start()
proflss.start()