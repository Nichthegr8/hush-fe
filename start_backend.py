import packages.connectors as connectors

llmss = connectors.llmServerSide()
proflss = connectors.profilesServerSide()

llmss.start()
proflss.start()