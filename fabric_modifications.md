# Fabric Modifications To Question Answerer

This spec details the modifications we will make to this question answerer tool to ground it to Fabric instead of to Bing Search. Remember to use the Microsoft Docs MCP server to look up any information about how to access the relevant APIs and agent tools.

This calls for the following modifications:

## Question Answerer

The Question Answerer agent will be modified to use Fabric as a tool instead of Bing Search. Similar to how it looks up Bing Search now, it will instead look up the Fabric connection using the environment variable called FABRIC\_CONNECTION\_ID. The Bing Search connection and tool will be removed.

The system message will be modified to indicate the presence of the Fabric tool, and will instruct the agent to use this tool for every question. It will also instruct the question answerer to return a blank response in the event that Fabric could not find any data for a given question.

## Answer Checker

The Answer Checker agent will be modified such that it has no tools. Instead, it will be given the original question and the Question Answerer's response, and will verify that the response does indeed answer the question. In the event that the Answer Checker finds the response invalid, the Question Answerer should be run again with a modified context, just as it is now. The default retries should be 10.

In the event that the Question Answerer's response is blank, the Answer Checker will not run at all.

## Link Checker

The Link Checker will be removed entirely, as it is not needed in this version.

## UI

The UI will be modified to remove the Documentation tab.

## Readme

The Readme will be updated to indicate the new function of this tool as an app to answer questions from a structured dataset represented by a Fabric Data Agent, and what env parameters it needs. The env.template file will also be modified to reflect what's supposed to be in the .env file - remember that you should never stage or commit a .env file though.