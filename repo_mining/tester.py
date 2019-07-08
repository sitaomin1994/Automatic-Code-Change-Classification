from create_table import CreateTable
from extract_commit_history import ExtractHistory
import json
# from ast import literal_eval
# import re

table = CreateTable("squad", "postgres", "SolomonLaine_11251994", "localhost")
table.mine_repo()
table.create_db("squad", "commit_history")


## last -- 4412e99999fc693ae67743622e84f06f3f7acdc4

# df_dict = table.get_commits_df()
# for items in df_dict["Netflix-Hystrix"]:
#     print(items)

# files = ['hystrix-core/src/test/java/com/netflix/hystrix/HystrixObservableCommandTest.java',
#          'hystrix-core/src/test/java/com/netflix/hystrix/UnsubscribedTasksRequestCacheTest.java',
#          'hystrix-dashboard/src/main/java/com/netflix/hystrix/dashboard/stream/UrlUtils.java',
#          'hystrix-dashboard/src/main/test/com/netflix/hystrix/dashboard/stream/UrlUtilsTest.java',
#          'hystrix-dashboard/src/main/com/netflix/hystrix/dashboard/sammy/just_file.java']
#
# build_reg = r"^.*(build|pom).*\.xml$"
# util_reg = r"^.*([u|U]til|[h|H]elper).*"
# test_reg = r".*[tT]est.*"
# for file in files:
#     if re.match(r"^.*\.java$", str(file)) and not(re.match(util_reg, str(file)) or re.match(test_reg, str(file))):
#         print(file)


# csha = "697fd66aae9beed107e13f49a741455f1d9d8dd9"
# app = "Netflix-Hystrix"
# extractor = ExtractHistory(app, csha)
# extractor.clone()

# with open("tmp_JSON/Netflix-Hystrix_4412e99999fc693ae67743622e84f06f3f7acdc4.json") as f:
#     output = json.load(f)
#
# print(json.dumps(output, indent=4, sort_keys=True))

