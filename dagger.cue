package main

import (
    "dagger.io/dagger"
    "universe.dagger.io/python"
)

dagger.#Plan & {
    client: {
        filesystem: {
            "./": read: {
                contents: dagger.#FS
                exclude: [
                    "**/__pycache__",
                    "**/*.pyc",
                    ".venv",
                    ".git",
                ]
            }
        }
        env: {
            MEM0_API_KEY:      string
            OPENROUTER_API_KEY: string
            OPENAI_API_KEY:    string
        }
    }
    
    actions: {
        deps: python.#Requirements & {
            source: client.filesystem."./".read
            packages: {
                pip: [
                    "mem0ai>=1.0.0",
                    "langchain>=0.1.0",
                    "langgraph>=0.0.10",
                    "pydantic>=2.5.0",
                    // ... other dependencies
                ]
            }
        }
        
        test: python.#Run & {
            input: deps.output
            command: "pytest"
            environment: {
                MEM0_API_KEY:      client.env.MEM0_API_KEY
                OPENROUTER_API_KEY: client.env.OPENROUTER_API_KEY
                OPENAI_API_KEY:    client.env.OPENAI_API_KEY
            }
        }
        
        build: python.#Build & {
            source: client.filesystem."./".read
            requirements: deps.output
        }
        
        serve: python.#Run & {
            input: build.output
            command: "python -m agent.main serve"
            environment: {
                MEM0_API_KEY:      client.env.MEM0_API_KEY
                OPENROUTER_API_KEY: client.env.OPENROUTER_API_KEY
                OPENAI_API_KEY:    client.env.OPENAI_API_KEY
            }
        }
    }
}
