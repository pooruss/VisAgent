# VisAgent: Empowering Financial Visualization in Business Intelligence

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Project Overview

VisAgent is an innovative framework designed to democratize data visualization through conversational interactions with Large Language Models (LLMs) and Multimodal Large Language Models (MLLMs). Users can articulate their visualization needs in natural language, and the agent interprets these requirements to generate insightful visual representations. This project addresses the on-demand personalized visualization problem, specifically in the financial sector.

## Key Features

- **VisAgent Framework**: A framework that facilitates the creation of personalized data visualizations through iterative improvements.
- **VisQ Dataset**: A collection of 65 financial datasets sourced from Kaggle, used for testing and evaluating the performance of visualization models.
- **VisEval Method**: A novel, automated evaluation method that uses advanced AI models to assess the generated visualizations, showing high correlation with human assessments.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/pooruss/VisAgent.git
    cd VisAgent
    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # For Windows users, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Modify the configuration in `assets/config.yml`, e.g. data path, agent configs, record directory, etc.
2. Run VisAgent to generate visualizations:

    ```sh
    python main.py --input data/financial_dataset.csv --query "Generate a bar chart showing the count of financial news headlines categorized as positive, neutral, and negative, styled like Salesforce"
    ```


## Datasets

The VisQ dataset includes 65 financial datasets, each accompanied by a unique personalized visualization query. This provides a robust platform for evaluating the performance of different data visualization models and systems.

- [Download VisQ Dataset](https://github.com/pooruss/VisAgent/data/VisQ_dataset.zip)

## Evaluation Method

We have developed a comprehensive evaluation protocol and method that utilizes advanced AI models to automatically assess the generated visualizations. This method has been validated to show a high correlation with human assessments, ensuring consistency and objectivity in the results.

## Experiment Results

The results on the VisQ dataset, evaluated using VisEval, indicate that VisAgent successfully addresses 52.4% of the queries, outperforming the ReACT baseline by 32.4%. These findings highlight the strengths and potential of using LLM-based agents for personalized data visualization.

- **Pass Rate**: 52.4%
- **Improvement Over Baseline**: 32.4%

## Contributing

We welcome contributions in various forms, including but not limited to:

- Submitting issues
- Performing code reviews
- Submitting pull requests

Please make sure to read our [Contributing Guidelines](CONTRIBUTING.md) before making a contribution.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or suggestions, please contact Shihao Liang (shihaoliang0828@gmail.com).

---

Thank you for your interest and support in the VisAgent project!