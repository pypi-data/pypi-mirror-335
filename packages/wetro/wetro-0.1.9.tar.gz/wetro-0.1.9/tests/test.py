from wetro import WetroRAG, WetroTools, Wetrocloud


def main():
    pass
    # # Test RAG operations via SDK
    # print("=== Testing RAG Operations via SDK ===")
    # rag_client = WetroRAG(api_key="your_api_key")
    # rag_client.collection.get_or_create_collection_id("test_collection_sdk")
    
    # insert_resp = rag_client.collection.insert(resource="https://example.com", type="web")
    # print("SDK Insert Response: %s", insert_resp.model_dump())
    
    # # Test basic query
    # query_resp = rag_client.collection.query(request_query="What is example.com?")
    # print("SDK Query Response: %s", query_resp.model_dump())
    
    # # Test streaming query
    # print("SDK Streaming Query Responses:")
    # stream_resp = rag_client.collection.query(request_query="Streaming test", stream=True)
    # for chunk in stream_resp:
    #     print(chunk.model_dump())
    
    # # Test structured query
    # structured_query = rag_client.collection.query(
    #     request_query="Structured output query",
    #     json_schema='{"result": "string"}',
    #     json_schema_rules=["rule1", "rule2"]
    # )
    # print("SDK Structured Query Response: %s", structured_query.model_dump())
    
    # chat_history= [{"role": "user", "content": "Tell me about example.com"}]
    # chat_resp = rag_client.collection.chat(message="Explain example.com", chat_history=chat_history)
    # print("SDK Chat Response: %s", chat_resp.model_dump())

    # delete_resource_resp = rag_client.collection.delete_resource(insert_resp.resource_id)
    # print("SDK Delete Resource Response: %s", delete_resource_resp.model_dump())
    
    # delete_resp = rag_client.collection.delete()
    # print("SDK Delete Response: %s", delete_resp.model_dump())
    
    # Test Tools operations via SDK
    # print("=== Testing Tools Operations via SDK ===")
    # tools_client = WetroTools(api_key="your_api_key")
    
    # categorize_resp = tools_client.categorize(
    #     resource="Match review: Example vs. Test.",
    #     type="text",
    #     json_schema='{"label": "string"}',
    #     categories=["sports", "entertainment"],
    #     prompt="Categorize the text to see which category it best fits"
    # )
    # print("SDK Categorize Response: %s", categorize_resp.model_dump())
    
    # generate_resp = tools_client.generate_text(
    #     messages=[{"role": "user", "content": "What is a large language model?"}],
    #     model="gpt-4"
    # )
    # print("SDK Generate Text Response: %s", generate_resp.model_dump())
    
    # ocr_resp = tools_client.image_to_text(
    #     image_url="https://images.squarespace-cdn.com/content/v1/54822a56e4b0b30bd821480c/45ed8ecf-0bb2-4e34-8fcf-624db47c43c8/Golden+Retrievers+dans+pet+care.jpeg",
    #     request_query="What animal is in this image?"
    # )
    # print("SDK Image to Text Response: %s", ocr_resp.model_dump())
    
    # extract_resp = tools_client.extract(
    #     website="https://www.forbes.com/real-time-billionaires/",
    #     json_schema='[{"name": "string", "networth": "string"}]'
    # )
    # print("SDK Extract Data Response: %s", extract_resp.model_dump())

if __name__ == "__main__":
    main()
