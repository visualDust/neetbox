---
sidebar_position: 1
---

# Useless yet NEETBox

__NEETBox contains useless code snippets for Deep Learning Researchers.__ The repository itself is still under construction and for now it has not much code inside. Nevertheless, we are always adding new code snippets. 

So here is the thing: I'm new to complex Computer Vision projects and I found myself writing duplicate codes somehow, about convolutional neural networking, figure ploting(for paper writing), visualizing, data processing, etc., in different projects. So I'm going to have code snippets for myself and for other beginners who would like to have one. Certainly there are a lot of extraordinarily frameworks with high performance models integrated in their model hub (or stuff like that). However, that's not what I really want. Personally, I would like to have a collection of standalone code snippets which you can easily plug into your code without importing heavy dependency or doing code migration.

## Installation

```bash
pip install neetbox
```
if error occured or you get some dependency issue, try:
```bash
pip install --index-url https://pypi.org/simple/ neetbox --no-deps
```
:::note
Why `--no-deps`? Because we had a hard time resolving the dependency :(  
Please manually install dependencies after you got errors  
:::

## If you want (Click to go):

- [x] [Simple Logging Utility](./logging/)
- [x] [Basic PyTorch Code Snippets](./torch-snippets/)

:::caution
Another problem here is that since the repository is still under construction, most of the codes do not have related docs. Sorry that some of the codes are massed up without regular comments on them. The docs will appear soon. 
:::

I would appreciate it if you would contribute your excellent tiny code snippets. There is no such ~~"Code of conduct"~~ here (lol) as long as the code runs buglessly. Leave your code here with simply a doc related to it would be helpful. Check [Paste your code!](/docs/develop) if you are interested.