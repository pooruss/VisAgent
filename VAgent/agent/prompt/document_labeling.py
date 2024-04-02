UNCERTAIN_BOX = """You are given a screenshot of a web page with interactive elements, circled by bounding boxes and their responding description. Here are some tasks you need to achieve:

1. You need to choose one bounding box and explain why you choose, which is the most uncertain to you, that means you are most unconfident what is the function of that element and you do not know what will happen if the element is clicked.

2. You need to summarize the current screenshot into an overview description, about what status is the current page, what important interactive elements are there, what information could the current page provide, what possible (but not limited) operations could be done to the current page, etc.

3. You need to summarize the history clicking trajectories and give one possible query, which match the history clicking choices. For example, given trajectories: Departments -> Engineering -> Teachers, the possible user could be: Find all the teachers and their contacts in Engineering departments.

*Things to notice*:
- Ignore those elements without text description. Choose within those with text description
- Text information is more accurate than the image information. Do not rely on your image understanding ability to see the bounding box indexes. Refer to the Bounding Boxes Description information to choose the box index.

Here are the given information:

Bounding Boxes Description:
{bbox_description}

History Clicking Trajectories:
{history}

Return format:

Overview: An overview of the current screenshot.
Reason: Explain which element you choose to be the mose uncertain one.
Box: the box index(an integer).
Query: Possible query to explain the history. Directly give the query.
"""

CERTAIN_BOX = """"""


API_BOX = """You are given a screenshot of a web page with interactive elements, circled by bounding boxes and their responding description. Here are some tasks you need to achieve:

1. You need to summarize the current screenshot(the first image) into an overview description, about what status is the current page, what important interactive elements are there, what information could the current page provide, what possible (but not limited) operations could be done to the current page, etc.

2. You need to choose one bounding box, which can be posibly formulate a function or a typical user task of the website in the future together with the history operations. Usually, choose those newly added bounding box which can be used to explore the next layer information, such as the first news page link appeared after clicking New, or the first teacher's contact after clicking Teachers.

3. You need to give one possible user task of the given history trajectories. For example, given trajectories: Departments -> Engineering -> Teachers, the possible user task could be: Find all the teachers and their contacts in Engineering departments. Also, School&Deparement -> School of Architecture, can form a function of 'Navigate to the website of School of Architecture'.

4. You need to predict the function of the element within the chosen bounding box, especially box without text description. For example, if box N does not have text description but have an element looks like a magnifier, then the functionality of this element is probably for searching information.

5. You need to summarize and describe the function of the last element clicked. You can compare the first image(current screenshot) and the second image(last screenshot) and find out what happened and what changes in the current screenshot to describe the element. For example, after clicking '1.news', the current screenshot include some latest news that the last screenshot did not have, or after clicking '2. '(thought there is no text description of the element), the current screenshot changed a little bit and shows a search bar, then the element '2. ' is used for navigating to search bar to conduct searching information. The summarization should include newly added information in the current screenshot.

6. You need to give a 'thought', to explain why you take the current action to achieve the user task. The thought should be in details, and may include some planning steps for future actions, and should include some GUI common knowledge.

*Things to notice*:
- Ignore those elements without text description. Choose within those with text description
- Text information is more accurate than the image information. Do not rely on your image understanding ability to see the bounding box indexes. Refer to the Bounding Boxes Description information to choose the box index.
- Directly give the function, e.g. 'Function: Find out information about ...'
- Sometimes there are some sliding information, which may appear to be different between the current screenshot and the last screenshot. Ignore the sliding information, and focus on the differences caused by clicking the last element.
"""

API_BOX_USER = """
Here are the given information:

Bounding Boxes Description:
{bbox_description}

History Clicking Trajectories:
{history}

Last Element:
{last_element}

Return format:

Overview: An overview of the current screenshot.
Box: the box index you want to explore for further function.(an integer).
Reason: Explain why you choose the element.
Element Prediction: Predict the functionality of the element(s) within the chosen box.
User Task: Possible function or user task to explain the history. Directly give the function.
Element Summarization: The summarized description of the last element.
Thought: Explain why you take the current action to achieve the user task.
"""