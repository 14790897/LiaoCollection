# 项目说明

<!-- toc -->

## 在线浏览

<https://whatot.github.io/leeao/index.html>

> 由 github action 驱动自动构建部署 master 最新版到 github page 中

## 所有权说明

**这个 github 帐号 whatot 并非原著者，whatot 只是将 wjm_tcy 编著的大李敖全集进行格式化，没有其它额外加工。
所有权利由 leeao 与 wjm_tcy 保持，此处仅为传播与留存。**
**编著者介绍见同目录“wjm_tcy.md”**

## 6.0 内容来源与贡献

本项目的 6.0 版内容迁移自
[GOLGO11/leeao](https://github.com/GOLGO11/leeao) 发布的
《大李敖全集 6.0》（发布提交 `8d5299b`），并在此基础上转换为适合
mdBook 的 Markdown 结构。上游仓库采用 MIT License；许可与版权声明见
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。该许可适用于上游仓库的整理成果，
不改变李敖原著及其他收录作品各自的权利归属。

《大李敖全集》由 wjm_tcy 长期整理，6.0 版得到 Jeff Ao、贾维斯、z、
小酥等敖友的资料支持。历次 OCR、校对和资料整理还参考或得到蛋蛋版、
funlin、john、yubar、jarvisdd、deepthroat、心灵心声、raphael、
我爱夏天在台湾、djwuwuwu、孤笑、不使人间造孽等贡献者的帮助。
GOLGO11（爱华山樱）维护并发布了 6.0 仓库及多种电子书格式。感谢所有
原始资料提供者、扫描者、OCR 整理者、校对者和传播者。

## 建库本意

我看 wjm_tcy 花费很多时间对“大李敖全集”进行整合，但是使用的 txt 格式，并且文件内无格式，不便于阅读，于是就对成品 txt 进行格式化。
最终组成一个 gitbook 项目，可以通过 gitbook 转化成 pdf、epub 或者 mobi，便于在各种设备上阅读。

gitbook 已经转向付费，于是迁移到 mdbook 实现。

我对作者的文章内容持保留态度，仅通过此项目减少编著的合集埋没的可能。

## 生成 html,epub,pdf

构建参考

- <https://github.com/rust-lang/mdBook>
- <https://rust-lang.github.io/mdBook/>
- <https://github.com/Michael-F-Bryan/mdbook-epub>
- <https://github.com/badboy/mdbook-toc>
- <https://github.com/badboy/mdbook-open-on-gh>
- <https://github.com/jontze/action-mdbook>

```shell
cargo install mdbook --version 0.5.4 --locked
cargo install mdbook-linkcheck --version 0.7.7 --locked
cargo install mdbook-toc --version 0.15.4 --locked
cargo install mdbook-epub --version 0.5.4 --locked
cargo install mdbook-open-on-gh --version 3.0.0 --locked

## 在book目录生成html版本，book/index.html。在浏览器中打开后，在index页使用右上角的print可以获得pdf版本。
mdbook build

## 生成epub，但是文件过于巨大，浏览困难，不推荐使用。
mdbook-epub --standalone .
```

## 文件处理流程

- using enca to convert files to UTF-8/LF
  `enca -L zh_CN -x UTF-8 */*.txt`
- check all the txt files's coding
  `find -type f -name '*.txt' | xargs file`
- delete unneeded lines
  `find -type f -name '*.txt' | xargs sed -i '/李敖研究网/d'`
- deleted trailing spaces
  `find -type f -name '*.txt' | xargs sed -i 's/[ \t\r ]\+$//'`
- delete all spaces
  `find -type f -name '*.md' | xargs sed -i 's/[ ]//'`
- rename all _.txt to_.md
  `for f in *.txt; do mv -- "$f" "${f%.txt}.md"; done`
