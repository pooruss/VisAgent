import gradio as gr
from VAgent.engine import VisEngine
from VAgent.environment import CodeEnvironment
from VAgent.memory import BaseMemory
from VAgent.config import CONFIG
import os
from PIL import Image

# 引入我们之前定义的 VisEngine 类和 run_one_step 方法
from VAgent.engine.interactive_visualize import VisEngine  # 确保引用正确的模块名

# 初始化组件
config = CONFIG  # 配置你的系统，假设 CONFIG 需要被实例化
engine = VisEngine(config=config)
env = CodeEnvironment(config=config)
short_memory = BaseMemory()

feedback = ""
history_code = ""

def run_visualization(query, file_path, step_count=0):
    global feedback
    global history_code
    # # 初始化或重置环境和记忆体
    # if step_count == 0:
    #     env.reset()  # 确保环境有 reset 方法
    #     short_memory.reset()  # 确保记忆体有 reset 方法
    print(file_path)
    env.data_path = file_path
    env.data = open(env.data_path, "r")
    env.data = env.data.read()[:500]
    # 运行一个迭代步骤
    while True:
        try:
            thought, visual_result, new_code, feedback = engine.run_one_step(query, env, short_memory, history_code, feedback, step_count)

            if feedback == "Exit":
                break

            step_count += 1
            image = Image.open(visual_result)
            history_code = new_code
            yield thought, new_code, image, feedback, step_count
        except RuntimeError as e:
            yield thought, new_code, None, str(e), step_count

# 创建 Gradio 界面
interface = gr.Interface(
    fn=run_visualization,
    inputs=[
        gr.Textbox(label="Enter your query", placeholder="Type your query here..."),
        gr.File(label="Upload your file"),
        # gr.Textbox(label="Enter feedback", placeholder="Provide feedback for the last iteration..."),
        # gr.Textbox(label="Reference Code"),
        gr.State(value=0)
    ],
    outputs=[
        gr.Textbox(label="Thought"),
        # gr.Textbox(label="Generated Code"),
        gr.Textbox(label="Generated Code"),
        gr.Image(label="Visualization Result"),
        gr.Textbox(label="Feedback"),
        gr.State()
    ],
    title="Visualization System",
    description="Enter a query to visualize data and provide feedback for iterative improvements.",
    theme="default",  # 选择一个主题,
    # live=True
)

# 启动服务器
if __name__ == "__main__":
    interface.launch()


import gradio as gr
import random
import time

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.Button("Clear")


    def user(user_message, history):
        return "", history + [[user_message, None]]


    def bot(history):
        bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
        history[-1][1] = ""
        for character in bot_message:
            history[-1][1] += character
            time.sleep(0.05)
            yield history


    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.queue()
demo.launch()
