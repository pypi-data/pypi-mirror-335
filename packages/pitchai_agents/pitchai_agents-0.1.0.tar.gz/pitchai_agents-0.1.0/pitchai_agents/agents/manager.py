from agent import code_read_agent, dev_agent
import asyncio
from code_ops.treemap import create_treemap
import os
import sys
import os
from code_ops.git_ops import commit_changes, push_branch, create_pull_request
from code_ops.codebase import setup_worktree
from agent.utils import set_simple_agent_logging

    
async def main(sys_argv_goal: str = None, branch_name: str = 'crawler_dockerfiled2'):
    set_simple_agent_logging()

    base_info = 'Note that this project uses SQLModel and NOT SQLAlchemy. We use a postresql database, so everything database-wise can be found in db.py. Use this when necessary. The id of the Product class is found as product_id. Dont change the already existing code. Use actual credentials for any services like meilisearch or database. This project consists of multiple parts. The crawler is important. The product matcher is important and the meilisearch_adder_service adds the items in the database that were matched to the instantsearchindex. '
    project_path = "/Users/sethvanderbijl/PitchAI Code/AI Price Crawler"
    interpreter_path = "/Users/sethvanderbijl/Library/Caches/pypoetry/virtualenvs/ai_price_crawler-6CKRPcSL-py3.11/bin/python"

    # project_path = "/Users/sethvanderbijl/PitchAI Code/AFASAsk"
    # interpreter_path = "/Users/sethvanderbijl/Library/Caches/pypoetry/virtualenvs/afasask_gzb_webapp-sdaNbJy7-py3.10/bin/python"
    # base_info = 'We do a lot of msg_actions.run_action with prompt paths to make gpt do tasks.'
    # goal = "We have now senior_dev_manager prompts. We also have 'afasask/agent/senior_dev_manager_test.py'. However, it does not function correctly yet. Investigate and make sure it works correctly."

    
    goal = sys_argv_goal
    goal = """Modify the `services/dockerfile-crawler` file until the Docker image builds successfully, the container runs without errors, and the internal Scrapy crawler executes correctly, 
        producing valid logs. The crawler must be able to locate and access all necessary files and resources within the container, including `airports.json` and `proxies.txt`, and utilize the environment 
        variables defined in `.env`. Your primary task is to get the crawler running inside a Docker container using the `services/dockerfile-crawler` Dockerfile. 
        You'll need to iteratively build, run, and modify the Dockerfile until the crawler functions as expected, generating correct logs. This is a practical, hands-on task focused on Dockerfile debugging and ensuring the
        crawler's dependencies and configurations are correctly set up within the container.\n\n**Key Considerations and Instructions (from Senior Devs):**\n\n1.  **Iterative Development and Testing:** Use `docker build` and `docker run` (with `--env-file .env`) 
        to test and debug. Use `subprocess` to automate the build and run process and check logs. Use `docker exec <container_name> /bin/sh -c \"ls -l /code\"` to inspect the container's filesystem and ensure files are where you expect them to be.\n\n2.  
        **`.dockerignore`:** The current `.dockerignore` may be excluding necessary files. Ensure it doesn't unintentionally exclude anything in `crawler/`, especially essential files like `airports.json`, `proxies.txt` and the spider definitions. **Crucially, the 
        `.env` file should NOT be ignored, or, alternatively, the environment variables must be passed to the container in some other way. The senior 
        dev strongly suggested that ignoring `.env` is a problem.**\n\n3.  **File Paths and COPY Instructions:**\n    *   The working directory inside the container
        is `/code`.\n    *   `airports.json` must end up in `/code` and currently the Dockerfile `COPY` command `COPY airports.json ./` appears correct.\n    *   `proxies.txt` must end up in `/code/crawler/crawler/proxies.txt`, and the Dockerfile 
        instruction `COPY . .` should take care of it as long as the current directory of the Dockerfile when building is the root and not services.\n    *   Verify the `COPY` commands in the Dockerfile and adjust them as needed to ensure all necessary files and directories
        are copied to the correct locations within the container. **It might be best to just copy the entire `crawler` directory.**\n\n4.  **Absolute Path in `spider.py`:** The crawler relies on `airports.json` specified with the absolute path `/app/airports.json`. This needs to be fixed. I 
        see two potential solutions:\n        1.  **Modify `spider.py`:** Change the absolute path to a relative path or use an environment variable. A relative path such as `'airports.json'` should work if the CWD is `/code`.\n        2.  **Modify the 
        Dockerfile:** Create a symbolic link inside the docker container so that `/app/airports.json` points to `/code/airports.json`.\n\n5.  **Environment Variables:**\n    *   Ensure all required environment variables (`DATABASE_URL`, `VASTAI_API_KEY`, `POSTGRES_*`, 
        `MEILISEARCH_HOST`, `MEILISEARCH_API_KEY`) are being correctly passed to the container using the `--env-file .env` option in `docker run`.\n    *   Consider defining default values for crucial environment 
        variables within the `settings.py` file to prevent the crawler from crashing if they are missing.\n\n6.  **Entrypoint:** The entrypoint is 
        `scrapy crawl dutyfree`. So it is important that it is able to find the spider.\n\n7.  **Essential files and directories:** I should copy the 
        following:\n    *   `crawler/crawler/proxies.txt`\n    *   `crawler/crawler/spiders/` (entire directory)\n    *   `crawler/airports_crawlable.py`\n    *   `crawler/crawler/airports.json`\n    *   `crawler/crawler/middlewares.py`\n    *  
        `crawler/crawler/settings.py`\n    *   `crawler/crawler/items.py`\n    *   `crawler/crawler/pipelines.py`\n    *   `crawler/scrapy.cfg`\n    *   `product_category_cache.json`\n    *   
        `http_cache.sqlite`\n\n**Workflow:**\n\n1.  **Build the Docker image:** Use `subprocess` to execute `docker build -f services/dockerfile-crawler .` and check for build 
        errors. Fix any errors in the Dockerfile.\n2.  **Run the Docker container:** Use `subprocess` to execute `docker run --env-file .env <image_name>` (replace `<image_name>` with the actual image name).\n3.  **Check container logs:** Use `subprocess` to
        execute `docker logs <container_name>` and look for errors from Scrapy or Python.\n4.  **Inspect the container:** If the crawler isn't working as expected, use `docker exec` to inspect the filesystem and verify that files are in the correct
        locations and that environment variables are set correctly.\n5.  **Modify the Dockerfile:** Based on the errors and logs, modify the Dockerfile 
        to fix file paths, dependencies, environment variables, or any other issues.\n6.  **Repeat steps 1-5 until the crawler builds, runs, and crawls correctly.**\n\n**Initial Focus
        (per Senior Dev Recommendations):**\n\n1.  **Review `.dockerignore`:** Make sure it's not excluding anything important, especially the `.env` file or the `crawler` directory contents. If `.env` is excluded, I'll need to find 
        another way to pass those environment variables to the container, as senior devs have said that the crawler relies on env vars.\n2.  **Address 
        absolute path in `spider.py`:** Change `/app/airports.json` to `airports.json` (relative path).\n3.  **COPY the `crawler` directory:** I will replace the 
        individual COPY commands with a single `COPY crawler crawler` command to ensure that all the crawler files are in the docker container.\n4.  **Verify WORKDIR:** Double-check that `WORKDIR /code` is present and correct.\n\n**Important Reminders:**\n\n*   Focus ONLY on 
        the `services/dockerfile-crawler` file and related configuration (e.g., `.dockerignore`). Do not modify unrelated files.\n*   The crawler is known to work when run directly, so the issue is with the Docker configuration.\n*   Use 
        `subprocess` for building and running the Docker container to automate testing.\n*   Use `docker exec` to inspect the container's filesystem 
        when debugging.\n*   Pay close attention to the logs for errors related to file paths, missing dependencies, or incorrect environment variables.\n*   Don't stop
        until you are fully sure the crawler works in the docker container and you have checked the logs. You must actually build and run the docker image yourself to confirm it works. Just use the ROOT user in the docker container, this command must be followed. Use the root user throughout the whole dockerfile. Don't create interactice sessions with the container it will crash, you can execute any command towards the container remotely though. You are allowed to move airports.json in the project if it helps."""
    
    worktree_path = setup_worktree(project_path, branch_name)
    treemap = create_treemap(worktree_path)

    output_summary= ''
    # output_summary =await code_read_agent.run_agent(max_steps=50, min_steps=3, global_goal=base_info+goal, treemap=treemap, repo_path=worktree_path)
    
    last_thought = await dev_agent.run_agent(max_steps=100, min_steps=3, global_goal=base_info+goal, codebase_summary=output_summary, repo_path=worktree_path, interpreter_path=interpreter_path, treemap=treemap)
    
    commit_changes(worktree_path, last_thought)
    push_branch(worktree_path, branch_name)
    create_pull_request('JoshuaSeth', 'AI-Price-Crawler', branch_name, last_thought)


if __name__ == "__main__":
    # print("Arguments received:", sys.argv)
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else 'crawler_dockerfiled-19'))