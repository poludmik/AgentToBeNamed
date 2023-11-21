from agenttobenamed import AgentTBN
import time
import pprint

start_time = time.time()

csv_path = "csvs/test_CSV_file_gdp.csv"
agent = AgentTBN(csv_path, gpt_model="gpt-3.5-turbo-1106")  # "gpt-3.5-turbo-1106", "gpt-4-1106-preview"


# query = "What is the maximum gdp?"
# query = "minimal value of happy rate"
query = "Find top 10 largest happiness indices and pieplot them."
# query = "Find the correlation between gdp and happiness index."
# query = "Create a barplot of the top 5 minimal values in the happiness index column."
# query = "Approximate the gdp to happiness index trend with a line and plot it."

# query = "average depth in the 'Plot' column" # Tags as 'general' text answer!!!

result, details = agent.answer_query_with_details(query)

print(pprint.pformat(details))

end_time = time.time()

print(f"Elapsed time: {end_time - start_time} seconds")





