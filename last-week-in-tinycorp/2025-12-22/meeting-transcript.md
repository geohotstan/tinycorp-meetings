# 2025-12-22 Meeting

### Meeting Agenda

**Time:** holiday edition, 9am Monday San Diego time
- company update
- llm app
- LLaMA training (grad acc, jit, flash attention)
- viz
- driver
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=5XHgivHDYPg)

### Highlights

- **[Holiday Week & Cloud Code Push](#geohot-000005)**: “No real meeting” this week; everyone should spend the holiday week playing with and leveraging Cloud Code, which he thinks will radically impact the industry in 2–3 years.
- **[Bounties Getting Nuked by AI Spam](#geohot-000005)**: Considering canceling bounties because submissions are “basically all AI spam”; AI gives skilled people leverage rather than making unskilled people skilled.
- **[Codex: Local vs Cloud Environment](#geohot-000129)**: Distinguishes Codex-on-your-computer vs Codex-in-the-cloud; says the cloud one is still “basically unusable” due to environment setup issues.
- **[Best Workflow: Cloud Code on Your Machine](#geohot-000149)**: Recommends running Cloud Code locally (“type cloud” in a directory); mentions open-source “open code” works similarly; likes it for practical tasks (e.g., fixing timezone) without reading manuals.
- **[Model Quality Matters (Opus 4.5 vs Others)](#geohot-000149)**: Says it’s “almost entirely the model”; Opus 4.5 is best in his testing; GPT-5.2 is “significantly worse” (but still better than open-source models he tried like QuenCoder/GLM 4.6).
- **[Make Code Readable for Humans → Readable for LLMs](#geohot-000512)**: Argues the same refactors that improve human readability improve LLM performance; TinyGrad’s small, public design makes it easier for LLM tools than large repos like PyTorch.
- **[Next Beam Search: Likely LLM-Centric](#geohot-000512)**: Says next year they’ll start on the next iteration of Beam Search and expects it to be “mostly just some kind of LLM.”
- **[Focus on Human-Facing Optimization APIs](#geohot-000631)**: Rather than “fully rendering/running” everything, he wants better APIs for humans to specify optimizations (e.g., splitting kernels), then LLMs can iterate like humans do.
- **[Viz as Machine-Consumable Artifact](#geohot-000727)**: Notes Viz can run with `viz=-1`/`viz=-2` to output a pickle without a server; describes Claude reading the pickle and iterating, motivating Viz outputs that machines can consume.
- **[LLM Productivity Needs Precise Specs & Fast Feedback](#geohot-000805)**: Emphasizes the future-critical code is what lets LLMs experiment “without fear of breaking things,” with quick checks for correctness—LLMs need precisely specified problems to avoid going off the rails.
- **[LLaMA Training Status: JIT Workaround + Multi-Device Wins](#chenyu-001046)**: Chenyu reports a workaround so gradient accumulation works under JIT; once that’s in place, CPU offload and multi-device “just work first try,” highlighting TinyGrad’s strength across backends.
- **[Planned JIT Refactor: Capture Less Aggressively](#geohot-001142)**: Geohot says current JIT “counts to three” then captures; he plans to make it see the same thing five times before capturing so “when I add the JIT things break” should mostly go away.
- **[Speed Strategy: Layer Tests → Throw LLM at Optimization](#geohot-001326)**: Wants good per-layer speed tests so they can “throw Claude at making that layer fast,” using both automated search and “hand search” for standout wins.
- **[Assembly Visualizer & Python RDNA Tooling Vision](#geohot-001630)**: Praises the new assembly graph; proposes a tasteful Python disassembler/assembler/simulator (moving away from LLVM) and pushing toward RDNA3 assembly as the first fully supported target.
- **[Endgame: Minimal Full AMD Driver + Better GPU Execution Views](#geohot-001939)**: Wants the stack to output correct GPU bitcode with a “complete full AMD driver” under 20k LOC; also wants views that show bottlenecks/latencies and tighter coupling with execution traces (mentions SQTT parser limitations).
- **[LLM Coherence “Doesn’t Lose the Plot” Claim](#geohot-002313)**: Says older LLMs lose the plot quickly but claims Opus 4.5 persists and stays coherent for “four hours and 49 minutes,” though Chenyu notes it can stay too coherent on a wrong path.
- **[Driver Update: MI350 Support + AQL/XCC Sync Issue](#nimlgen-002454)**: Nimlgen reports working on MI350 support and driver stability; describes an AQL queue reset/reupload issue that fails to sync across XCCs (also seen in AMD’s driver), with a current workaround of reusing the queue.
- **[Cleanup & Consolidation: Delete Old Infra + One LLM Home](#geohot-003351)**: Encourages deleting old code in extra/external (e.g., ShapeTracker/lazy buffer); wants to delete other LLM implementations and consolidate on TinyGradApps LLM (mentions it supports LLaMA, Qwen, Alma, and a compact MOE).
- **[Replace heuristics.py with RLVR-Trained LLM Search](#geohot-003446)**: Proposes using “RLVR” (reinforcement learning from verifiable rewards) to fine-tune a coder model on kernel performance traces; imagines an LLM that one-shots optimizations, with “search” being how long/many shots (1/3/10) you run it.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=5XHgivHDYPg&t=0)]
Quickly, Ghost Release, company update.

##### **Geohot** [[00:00:05](https://www.youtube.com/watch?v=5XHgivHDYPg&t=5)]
Yeah, kind of Christmas. No real meeting this week. Everybody should be playing with and leveraging Cloud Code. I think that.. Look, it's not that good yet, but this is the first one that's usable. And I think it's going to impact the entire industry so radically in the next two to three years. Like, I'm almost to the point where I'm thinking about canceling bounties. What I get for bounties now is basically all AI spam. And it's not like.. AI is such a jagged thing, right? Like, the problem is that these people are people who never could have completed bounties on their own. And I don't think that AI is going to.. take less skilled people and make them more skilled. I think AI is going to take more skilled people and give them more leverage. So it's interesting.

##### **Geohot** [[00:01:04](https://www.youtube.com/watch?v=5XHgivHDYPg&t=64)]
Yeah, just kind of how that works. Have you tried the latest Codex? Yeah.

##### **Geohot** [[00:01:12](https://www.youtube.com/watch?v=5XHgivHDYPg&t=72)]
What do you think? You liked it better?

##### **Chenyu** [[00:01:16](https://www.youtube.com/watch?v=5XHgivHDYPg&t=76)]
Oh, I haven't tried. But I remember you tried this before. And I saw some comments saying it might be better. So I was just curious. If you haven't tried. I haven't. I probably will try at some point.

##### **Geohot** [[00:01:29](https://www.youtube.com/watch?v=5XHgivHDYPg&t=89)]
Okay. So there's the Codex. There's the Codex that runs on your computer. And there's the Codex that runs in the cloud. The Codex that runs in the cloud is still basically unusable because its environment is not set up.

##### **Chenyu** [[00:01:41](https://www.youtube.com/watch?v=5XHgivHDYPg&t=101)]
But also has a run time. You also use the cloud code that runs in the machine, right? Not the browser one. Or you use both.

##### **Geohot** [[00:01:49](https://www.youtube.com/watch?v=5XHgivHDYPg&t=109)]
I use the cloud code entirely that runs on the machine. So you run on the machine. You type cloud. And it'll run in a directory. There's also an open source version called open code. That seems to work pretty much as well as cloud code. But that's really just all about the model. It's Opus 4.5 that's actually better. But the best flow I've found is the cloud code that runs on your machine. And it's to the point. Like this morning, I had to change my time zone. I just ran cloud and said fix my time zone. And it ran the right time zone control command to do the time zone. Because I'm not going to read the manual. Cloud can do it for me. And it's great. So yeah. No, it's really good. I mean, it can run for a long time. If you give it a task that it can't mess up, that doesn't require taste. If you're just like fix this test, it will repeatedly try things until it fixes the test. And it's good at that. If you ask it to refactor this, it'll give you garbage. It's the same as any of these other AI things. It won't refactor it to make it nice. You have to do a whole lot of polish on the code before you can submit it. That's all still true. But if you just want something to work and you want it to repeatedly throw itself at it for two hours, it will do that. Which is cool. Yeah, it also seems almost entirely to be the model. Because I tried all the other models. I tried GPT-5.2 in cloud code. I tried GPT-5.2 in open code, which is supposed to be the second best model. And it's.. Significantly worse. Though it's still more usable than any of the open source models I've tried. I tried QuenCoder. I tried GLM. They just came out with a new GLM today. So I haven't tried that one yet. But I tried GLM 4.6 and it's not good. But I think this is the most radical thing that's going to change our company. I also think that we've structured ourselves incredibly well to take advantage of this. For Pathy's blog, an interesting post. It was about how basically individuals are getting way more benefit from AI than companies. Because companies are set up in these dodgy ways. It's difficult to change things at companies. I'm not talking about Google. I'm sure Google is doing fine. But your average company is just.. Even TinyCorp is better set up than Comma to take advantage of this stuff. Comma's got to deal with security issues. And not security issues. Someone's going to leak some information. Security issues. If you just run Claude in the Comma infrastructure, we'll have to delete all the data. Yes. Whereas the tiny boxes are designed not to be trusted. TinyGrad is designed to be entirely public. It's short. When you try to use these things on bigger repos, they get lost. Yes. It's amazing how good they are. You just read the three files in TinyGrad. It all makes sense. I tried to get them to do some stuff in PyTorch. It's all over the place.

##### **Chenyu** [[00:05:00](https://www.youtube.com/watch?v=5XHgivHDYPg&t=300)]
Some of it we can probably do better. From time to time, we still try to read the whole file and it says the file is too big or something like that. Or cannot probably find the right thing.

##### **Geohot** [[00:05:12](https://www.youtube.com/watch?v=5XHgivHDYPg&t=312)]
So QuadCode will do a good job reading chunks of the file. But yeah, I think the same refactors that make codebases readable for people make codebases readable for LLM. I can believe that. Yeah, basically. I mean, this is our general, this has been Comma's general take on AI. It's like, you know, Elon's talking about how to get the precise picture, precise pixels from the camera sensor into the AI. And our take has always just been make the picture look good for a human and it looks good for an AI. The same thing. So yeah, I think that's all true. But, and then I'm also excited to start, I think next year we're going to really start on what the next iteration of Veeam Search is going to be. And it's going to be mostly just some kind of LLM.

##### **Chenyu** [[00:05:59](https://www.youtube.com/watch?v=5XHgivHDYPg&t=359)]
Do you think we need to, I guess, does it need to render stuff to know what's good? Or it can do better than that? Oh, there are multiple layers to this, right? So for now, what we are doing is render the code, run the code to get your data. But then we will think about like how to simulate this through other proxy then do that.

##### **Geohot** [[00:06:31](https://www.youtube.com/watch?v=5XHgivHDYPg&t=391)]
Uh, I don't think that that, I think that, so like all of these LLM things, when you compare something like Stockfish to a chess, uh, with LLM based chess engine, I think that these steps will be slower, but each step will be better. Um, like it will spend more time thinking about these steps. So I'm not worried about it fully rendering, fully running on the GPU, getting like full access. All of that stuff. So I almost think what we want to focus on instead of making a better automated search is making the API to the human, to specify all of these things as good as possible. So if you want to like split a kernel, right? Like we want to make that, that API as simple as possible for a human to use. And then the LLM can just try the same thing that a human would do. Yeah.

##### **Chenyu** [[00:07:19](https://www.youtube.com/watch?v=5XHgivHDYPg&t=439)]
We still don't know. We still don't have proper APIs for like multi-reduce and stuff like that. Or, but.

##### **Geohot** [[00:07:27](https://www.youtube.com/watch?v=5XHgivHDYPg&t=447)]
Um, what do you mean? Oh yeah. To specify, yeah. To specify what's used and what's not used. I mean, we like have contiguous, but I think we can do a lot better. Um, I also think it's interesting. I let Claude, we have a, you can run Viz equals minus one or Viz equals minus two now, and that will just output the pickle file without running a server. And then Claude will happily run that, looked at the pickle file and then iterate on that loop itself. So, you know, we just want to start thinking about, you know, what, what, what, what would be the best way to run a server. And then we can try to figure out how Viz can also be consumed by, uh, by machines.

##### **Chenyu** [[00:07:59](https://www.youtube.com/watch?v=5XHgivHDYPg&t=479)]
I also see Claude trying to debug equals to some number and try to read the output of that.

##### **Geohot** [[00:08:05](https://www.youtube.com/watch?v=5XHgivHDYPg&t=485)]
Yeah. I mean, it's, it's, it's great. Like if you make this stuff good for humans, you make this stuff good for LLM for the most part. Um, I really liked your, your comment about how, uh, yeah, we should look at how Claude code tries to use tiny grad and then make it intuitive to the LLM because if intuitive to the LLM, it's intuitive to humans. Um, yeah. But I think overall we're in a great place to, I think that the code that's really going to be important in the future is code that allows the LLMs to experiment without fear of breaking things. LLMs are, can code a hundred times faster than humans. They can try lots and lots and lots of things, but what you don't want, what you want them to have is a very quick way of saying, is this the correct thing or not? Like it's more important for the LLM that the problem is precisely specified because otherwise they kind of go off the rails. Whereas a human can like think much more big picture about, oh, well, okay, this is obviously like what, you know, nobody would want that one. People would want it done like that.

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=5XHgivHDYPg&t=553)]
Where the LLMs happy to do it any other way.

##### **Chenyu** [[00:09:16](https://www.youtube.com/watch?v=5XHgivHDYPg&t=556)]
I know.

##### **Geohot** [[00:09:21](https://www.youtube.com/watch?v=5XHgivHDYPg&t=561)]
Uh, makes sense. Yeah.

##### **Chenyu** [[00:09:24](https://www.youtube.com/watch?v=5XHgivHDYPg&t=564)]
Where's my MLM translama for me?

##### **Geohot** [[00:09:28](https://www.youtube.com/watch?v=5XHgivHDYPg&t=568)]
Yeah. I mean, it's only two weeks. Just try it. Try it. Try it. See how fast Claude can just tear through these bugs.

##### **Chenyu** [[00:09:39](https://www.youtube.com/watch?v=5XHgivHDYPg&t=579)]
Yeah. I'll try. I'll try. I'll try these later. I just don't want to run this on my three.

##### **Geohot** [[00:09:47](https://www.youtube.com/watch?v=5XHgivHDYPg&t=587)]
Oh, you don't want to run the Claude there? You can. I don't know. I don't know. It's probably fine.

##### **Chenyu** [[00:09:53](https://www.youtube.com/watch?v=5XHgivHDYPg&t=593)]
I don't know. I don't know. I don't know. I don't know. Okay.

##### **Geohot** [[00:09:54](https://www.youtube.com/watch?v=5XHgivHDYPg&t=594)]
It's I've just kind of learned to trust it. Like, I think it's like fine. It's like, what's the worst it could really do on the computer? It's not like we have like big secrets.

##### **Geohot** [[00:10:03](https://www.youtube.com/watch?v=5XHgivHDYPg&t=603)]
Yeah. Yeah.

##### **Geohot** [[00:10:10](https://www.youtube.com/watch?v=5XHgivHDYPg&t=610)]
Just give it, give it, give it a try. And like, especially if you have something that just isn't working and you want like, like it's very, very good at spending two hours trying the same thing over and over and over again. And then, uh, telling you that you're not going to be able to do it. And then, uh, telling you why something doesn't work.

##### **Chenyu** [[00:10:28](https://www.youtube.com/watch?v=5XHgivHDYPg&t=628)]
Yeah. I mean, my take is the stake of trying that is very, very low anyway. So even if the probability of a successful outcome is not that high, it's still good.

##### **Geohot** [[00:10:39](https://www.youtube.com/watch?v=5XHgivHDYPg&t=639)]
Yeah. Yeah.

##### **Chenyu** [[00:10:46](https://www.youtube.com/watch?v=5XHgivHDYPg&t=646)]
I think for, for the LLaMA training, what I have learned a lot is once. The JIT is workaround. I find a workaround so that the gradient accumulation can work in JIT. It's very weird. I don't know the root cause, but, uh, as long as the workaround is good, it's good. Then all the offloading to CPU and the multi device stuff are just work first try. I think that's the part tiny grid works the best for like multi backend and stuff like that. Right.

##### **Geohot** [[00:11:20](https://www.youtube.com/watch?v=5XHgivHDYPg&t=680)]
So birds now. Okay.

##### **Chenyu** [[00:11:23](https://www.youtube.com/watch?v=5XHgivHDYPg&t=683)]
So, uh, I think that's the part that works the best for like multi backend and stuff

##### **Geohot** [[00:11:25](https://www.youtube.com/watch?v=5XHgivHDYPg&t=685)]
like that. Yeah.

##### **Geohot** [[00:11:26](https://www.youtube.com/watch?v=5XHgivHDYPg&t=686)]
I'm working on a, I'm working on a refactor of the jet that that's gonna pick. Uh, sure.

##### **Chenyu** [[00:11:35](https://www.youtube.com/watch?v=5XHgivHDYPg&t=695)]
It's less of a, but it's always nice to, to, to make it better.

##### **Geohot** [[00:11:42](https://www.youtube.com/watch?v=5XHgivHDYPg&t=702)]
Yeah, no, I think that the, the, if your only problem is like when I add the JIT things break, this should almost entirely go away. Um, because I'm going to not. Yeah. The jet currently just counts to three and says on the third one, it can capture. This is absurd. I'm going to make the JIT see the same thing five times before capturing. It'll be fast.

##### **Chenyu** [[00:12:09](https://www.youtube.com/watch?v=5XHgivHDYPg&t=729)]
Okay. Yeah. So the flash attention probably need to wait until was parrot is back. Uh, I think some of it, but there are still like devices. You probably didn't try like multi device. Yeah. Plastic, plastic devices and stuff like that.

##### **Geohot** [[00:12:27](https://www.youtube.com/watch?v=5XHgivHDYPg&t=747)]
So I think, uh, I let it try for awhile. Maybe I didn't try hard enough. It's just wrong.

##### **Geohot** [[00:12:44](https://www.youtube.com/watch?v=5XHgivHDYPg&t=764)]
I don't know.

##### **Geohot** [[00:12:46](https://www.youtube.com/watch?v=5XHgivHDYPg&t=766)]
Yeah.

##### **Geohot** [[00:12:47](https://www.youtube.com/watch?v=5XHgivHDYPg&t=767)]
Whenever I try to give it refactors that are too big, it doesn't succeed at, uh, so Yeah. But if it needs to find one line, it'll find that one line. Yes.

##### **Chenyu** [[00:13:03](https://www.youtube.com/watch?v=5XHgivHDYPg&t=783)]
Yep. I think then with all these techniques, we should be pretty good at least to train AB. So I'm testing some of the eval stuff now, making sure the whole flow works, fixing the logging and stuff. So that looks pretty good.

##### **Geohot** [[00:13:26](https://www.youtube.com/watch?v=5XHgivHDYPg&t=806)]
The sooner we can get good tests up on one layer for the speed of one layer, we can also just throw Claude at making that layer fast. We can hand search to find the most incredible stuff.

##### **Chenyu** [[00:13:43](https://www.youtube.com/watch?v=5XHgivHDYPg&t=823)]
So loads kind of needs fresh attention anyway, because you would need that layer to be representative. Yeah. And now every bottleneck is on tension. So I guess the tension is the fast GEMM. So making GEMM fast is also part of that.

##### **Geohot** [[00:14:01](https://www.youtube.com/watch?v=5XHgivHDYPg&t=841)]
Agreed.

##### **Chenyu** [[00:14:03](https://www.youtube.com/watch?v=5XHgivHDYPg&t=843)]
Yeah. But I think overall training looks fine. It's not the first time we do this. Probably not the last time we do this.

##### **Geohot** [[00:14:12](https://www.youtube.com/watch?v=5XHgivHDYPg&t=852)]
So just iterate on it. Wait. Why don't we try anything here? You say something Biznow has the assembly visualizer. You can try it on any AMD back end or with mock GPU. mazur verstehen mittel export Will also post a picture on Sorry? Have you tried Cloud hamburger? What do you think? Oh, Cloud Code. I use ChatGPT, and I'm used to it. Oh, Codex? No, I just type into ChatGPT what I want.

##### **Geohot** [[00:15:06](https://www.youtube.com/watch?v=5XHgivHDYPg&t=906)]
Try Cloud Code. If you don't have an account, you can pull my credentials off of PR9. It's a lot better. So my friend at the Kama NIP party works at Anthropic, and he dissed me in a way that really got through to me, because I was doing the same thing as you. I just mostly copy and pasted into ChatGPT. He's like, oh, you're using AI like how people used AI a year ago. Everyone's moved on to this new workflow now, and I'm like, okay, okay, I'll try it. It's worth trying. You may think it's still not good enough, but I found the flow to be a lot better than what I used to do,

##### **Geohot** [[00:15:52](https://www.youtube.com/watch?v=5XHgivHDYPg&t=952)]
which is just pasting into ChatGPT.

##### **Chenyu** [[00:16:01](https://www.youtube.com/watch?v=5XHgivHDYPg&t=961)]
Yeah, so I think it's not a replacement to how you work. It's a replacement to pasting something into ChatGPT and ask questions.

##### **Geohot** [[00:16:18](https://www.youtube.com/watch?v=5XHgivHDYPg&t=978)]
Also, trying is very low, so give it a try. Yeah, makes sense.

##### **Chenyu** [[00:16:24](https://www.youtube.com/watch?v=5XHgivHDYPg&t=984)]
If it doesn't work for you, it's fine. No big deal. But it's worth trying.

##### **Geohot** [[00:16:30](https://www.youtube.com/watch?v=5XHgivHDYPg&t=990)]
This graph looks great. This is much more readable to me than what was there before. I mean, I like being able to just zoom in on the thing, too. I probably spent like 10,000 hours in IDA, and I'm like, oh, I'm going to do this. Probably even more. It feels cool. Some other things that you could add, but things that we want to start basically, I don't know if you saw, I have a PR from a while ago building a Python DSL for the RDNA pre-assembly language. So you're just using, how are you generating this right now, the graph?

##### **Geohot** [[00:17:08](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1028)]
I'm just parsing the assembly using LLVM. You're parsing the assembly, the text assembly, or? The text assembly, yeah. Yeah, I mean, what we want is like, yeah, go ahead.

##### **Geohot** [[00:17:27](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1047)]
Yeah, how are you finding like where the block ends and stuff? Like, how are you finding the jump destination?

##### **Geohot** [[00:17:34](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1054)]
Oh, I just parsed the operands right from the text.

##### **Geohot** [[00:17:39](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1059)]
Okay, so it's all CAA. Yeah. I mean, we got to like, basically what I want to write, and maybe you want to, this has to be done so tastefully, but start to write like basically a disassembler in Python. I mean, we don't just want it to be a disassembler. We want a disassembler, an assembler, and a simulator, all in Python. That has like a really good, to move away from kind of the LLVM. I mean, it would be all the same like front-end code, but just like, so you're parsing from the text,

##### **Geohot** [[00:18:09](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1089)]
and you're like searching for the, like the label with the colon? No. LLVM gives you like an address table.

##### **Qazalin** [[00:18:24](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1104)]
This program counter maps to this instruction, and then you just add stuff at the offset and find the program counter.

##### **Geohot** [[00:18:33](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1113)]
Yeah, I feel good. But yeah, no, I mean, overall, overall, I like this. So another cool thing that IDA has is you can click on a register, like because these are the features that I want to get. Like you can click on a register, and then it'll light up all other uses of that register. Download the demo of IDA if you haven't.

##### **Geohot** [[00:18:57](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1137)]
Yeah, download the demo of IDA and try it,

##### **Geohot** [[00:19:00](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1140)]
because we want this to be a full like environment to see this. Like I'm looking at this, I'm looking at just the test GEMM right now. And it's amazing how it never uses the dual ALU. Like they're all just single FMAC. Why?

##### **Geohot** [[00:19:17](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1157)]
Oh. Yeah, but. No, it's good.

##### **Geohot** [[00:19:23](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1163)]
I think we got it. We got to start really pushing for RDNA 3 assembly, though. It's clear that RDNA 3 is going to be the first one.

##### **Geohot** [[00:19:34](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1174)]
Yeah, move away from LLVM. Full.

##### **Geohot** [[00:19:39](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1179)]
It's complete. It's fully complete when we're done with that. It's like I don't even want LLVM to be assembled. I want the entire thing to like output the correct bitcode to the GPU under 20,000 lines, the complete full AMD driver.

##### **Geohot** [[00:19:58](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1198)]
Oh. Yeah, how's the speed of the GEMM going? How fast is the GEMM on MIT 50? So,

##### **Qazalin** [[00:20:10](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1210)]
baseline, it's a lot of 1.4 times faster than our baseline. The hand coded one. I'm sure there's some secret one that's faster, but we'll just find it.

##### **Geohot** [[00:20:24](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1224)]
But I have like the infrastructure to like run assembly and see everything.

##### **Qazalin** [[00:20:31](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1231)]
I spent way too much time figuring out what headers going to the LLVM thingy for MI3. You just have, you just have to specify what is the will do what, which is kind of cool talking about the jako,

##### **Geohot** [[00:20:50](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1250)]
but why like the bitcode has been 5.5 times faster than the04 you wereow, which is clamshell 50 more faithful.

##### **Qazalin** [[00:20:52](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1252)]
But your DNA functions, your RNA is 15 times faster than the Seminal highly right? When you get past that Map attack with Aha, And then once you're at this level of comfort you're like, It's perfect for the stream. Because we have the webmaga, Does it work.

##### **Geohot** [[00:21:03](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1263)]
That's all it can do is

##### **Geohot** [[00:21:05](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1265)]
I mean, I'm looking at this disassembly too, and I'm imagining like something showing me which of these lines is the bottleneck, how long each one of these loads is taking, these S weight counts, like which loads is it waiting for?

##### **Geohot** [[00:21:25](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1285)]
Oh, yeah, that one. I also love that. Yeah.

##### **Geohot** [[00:21:30](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1290)]
Yeah. And I think this also like comes down to the, so have you looked at my SQTT parser? It doesn't work on RDNA 4, but on RDNA 3, it's really interesting because it doesn't give you all the information. Like it doesn't ever give you a program counter. It doesn't ever tell you where the instruction pointer is. It just tells you what instructions are executed, but that's enough to reconstruct all the data. So like, I mean, what we want is to just like tightly couple all of this. We want this assembly view to really show you this is how the GPU executed these instructions. And that's what will let us deliver fast stuff. And then we should also be thinking always about the, yeah. Try quad code. You know what? If no, this is a holiday week. If no tiny grad work gets done this week, it's totally fine. Play with quad code on literally anything and realize that what we have to do is like make tiny grad usable to LLM. So just like, yeah, basically like the underlying APIs that Viz uses. It should also be accessible to LLM.

##### **Geohot** [[00:22:40](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1360)]
Yeah. Imagine it just loops with the counters until it makes them fast.

##### **Geohot** [[00:22:47](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1367)]
Yeah. It's just going to sit there and be like, oh, I see a three cycle delay in this ALU. If I permute these two instructions, maybe it will go away. Let me try it. And then it tries it and it's like, okay, that delay has been removed.

##### **Geohot** [[00:22:59](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1379)]
Let's move on to the next thing. Sounds like a feedback loop LLMs can do.

##### **Qazalin** [[00:23:08](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1388)]
Like my problem with LLMs is always like it goes off bait very fast. Yes.

##### **Geohot** [[00:23:13](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1393)]
Yes. And that was all entirely true until Opus came out. Opus 4.5 is the first one this is not true for.

##### **Geohot** [[00:23:23](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1403)]
Look at this study. So it just persists.

##### **Geohot** [[00:23:32](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1412)]
And not only does it persist, it doesn't break because I agree with you. LLMs break in this exact way. They will very quickly like lose the plot, but this one claims that it stays

##### **Geohot** [[00:23:44](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1424)]
coherent for four hours and 49 minutes.

##### **Chenyu** [[00:23:55](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1435)]
Sometimes it's too coherent that if the first few tries is wrong, it will just continue on that attempt and the easiest way to recover is just the start of it.

##### **Geohot** [[00:24:05](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1445)]
This is just a very new strategy. Yeah. Yeah. I mean, it's not perfect. And it requires some handholding, but it doesn't lose the plot like the other ones anymore. I think we've got holiday week for this. Let's play with it. Just tell us, make the GEMM fast. Maybe we'll make the GEMM fast.

##### **Chenyu** [[00:24:42](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1482)]
Okay.

##### **Nimlgen** [[00:24:54](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1494)]
Yeah, so I've been working on MI350 support for AM and the stability of the state in general. So yeah, we actually have..

##### **Geohot** [[00:25:10](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1510)]
Have you tried Claude's code?

##### **Nimlgen** [[00:25:13](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1513)]
Yeah, I did.

##### **Geohot** [[00:25:15](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1515)]
What do you think?

##### **Nimlgen** [[00:25:20](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1520)]
Yeah, it's helpful, but I think I haven't used it much. I don't have a strong opinion yet.

##### **Geohot** [[00:25:30](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1530)]
Yeah. Yeah, it's.. Good.

##### **Nimlgen** [[00:25:37](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1537)]
I think doing some research and just trying things. Actually, I just tried to fix the AQL stuff. Because actually, even the AMD GPU driver has the broken.. Has the broken AQL. Like, basically the issue if you just reset the queue, the AQL queue, and just re-upload it with the new data, it just does not sync with.. With different XCCs. So.. Yeah, I don't know. Like, Claude just tried for several hours, but I know nothing useful.

##### **Geohot** [[00:26:21](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1581)]
Yeah. No, sometimes if it can't make.. If it's like one thing that has to just get or doesn't get, it often can't get. But if it's the kind of thing where it can write S and hit intermediate, it can get it. If it's the kind of thing where it can write S and hit intermediate stuff, it's pretty good. But yeah, no, with a lot of hardware stuff. Yeah, I can see how it can just continually miss.

##### **Geohot** [[00:26:49](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1609)]
Yeah. So yeah, but..

##### **Geohot** [[00:26:55](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1615)]
Yeah, if it involves deep reasoning, it's not good at that. If it involves spamming over and over again, it's good at that.

##### **Geohot** [[00:27:04](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1624)]
Yeah.

##### **Nimlgen** [[00:27:05](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1625)]
I also found it's like not really good reading AMD GPU driver. So like, as a reference, so I need just to point these specific places as a reference for the code.

##### **Geohot** [[00:27:21](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1641)]
But yeah. Yeah. Maybe the code base is too big.

##### **Qazalin** [[00:27:31](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1651)]
So yeah, I'll.. Oh, cool.

##### **Nimlgen** [[00:27:36](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1656)]
Maybe the code base is too big. Maybe the code base is too big. Yeah. Yeah. So I'm still going to do some runs this week to make sure that it's stable and it's ready for LAMA training. And yeah, also I'll reduce speed. I started.. I've started to work on XGMI, like instead of PCI SDMA. But.. No results yet. So yeah. I'll.. I'll look into these.

##### **Chenyu** [[00:28:10](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1690)]
Cool.

##### **Geohot** [[00:28:10](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1690)]
But great. So we have a driver that works on both 300 and 350. We can unload the stuff?

##### **Geohot** [[00:28:20](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1700)]
Yeah. Is it better or worse? I'll..

##### **Nimlgen** [[00:28:28](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1708)]
I mean, the main issue we had is the stability with the AMD GPU driver. I mean, the main issue we had is the stability with the AMD GPU driver. So yeah, I just need some time to validate these on AMS. But yeah, I mean.. And although the warm..

##### **Geohot** [[00:28:42](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1722)]
The warm reset stuff is fixed?

##### **Geohot** [[00:28:45](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1725)]
Yeah. Great. Cool. Yeah. No, I mean, it's..

##### **Geohot** [[00:28:56](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1736)]
It's nice that when we hit bugs on this, we'll be able to actually debug them. I'm not familiar with what specifically is the AQL problem. You're saying that it's not syncing across the XCCs? Like if there's a cache that's not being validated?

##### **Nimlgen** [[00:29:11](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1751)]
Yeah, that also was fixed. Yeah. Not the cache, but.. Actually, I don't know. There is something inside the GPU actually to sync these XCCs. And..

##### **Geohot** [[00:29:22](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1762)]
I still haven't found this. I looked quite a bit, too.

##### **Nimlgen** [[00:29:27](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1767)]
Yeah. So.. Actually, I don't know. I just tried to reset a lot of different parts of the GPU. But actually, the issue is that if you just run some compute on the queue.. So I don't know. Maybe there is some counter inside on the GPU. So actually, if you just reupload the queue and you just start running it from the beginning, it will not sync like the same amount of compute you've run the previous.. Like the previous time.

##### **Chenyu** [[00:29:59](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1799)]
Yeah.

##### **Nimlgen** [[00:30:01](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1801)]
So yeah. And actually, that's the issue with AMD GPU. If you manually load the MQD, not with MESS, but manually, so they have the same issue. So probably, we're not cleaning something and they also not cleaning up something. But actually, currently, there is a workaround. We just reused the queue and it works fine.

##### **Geohot** [[00:30:26](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1826)]
Wait. Do the CDNA cards even have MESS?

##### **Nimlgen** [[00:30:30](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1830)]
Yeah. It's not like MESS. I mean, yeah. It's not like a specific IP as on the GFX 11. But yeah, they have something similar.

##### **Geohot** [[00:30:44](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1844)]
And it's also called MESS. But yeah.

##### **Chenyu** [[00:30:56](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1856)]
Cool.

##### **Qazalin** [[00:30:59](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1859)]
Yeah. More validation. XTMI. Sounds good.

##### **Geohot** [[00:31:12](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1872)]
I'd kind of like to just stick plug code on reverse engineering the MEC.

##### **Geohot** [[00:31:19](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1879)]
I put some time into it. And we have a full.. I'm really happy with the progress on the USB chip. We have everything figured out on that chip now, if you've seen that repo.

##### **Geohot** [[00:31:29](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1889)]
Yeah.

##### **Nimlgen** [[00:31:36](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1896)]
So maybe something based on the silvered package, if you need theikuit contraption. Basically just like any other stuff.

##### **Geohot** [[00:31:56](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1916)]
 hitting bigger addresses on the GPU?

##### **Geohot** [[00:32:01](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1921)]
Like you didn't try to hit stuff on the bar? No, I don't.

##### **Nimlgen** [[00:32:11](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1931)]
I mean, even maybe in our current implementation, it's not the maximum size. It should be 512k, I think. And maybe we use only 256.

##### **Geohot** [[00:32:26](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1946)]
I think we actually only use 64. Oh, yeah. Maybe 64, yeah.

##### **Geohot** [[00:32:39](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1959)]
Yeah, we can play with this later. We're going to have it in Hong Kong. Tom is working on the boards. We'll have boards that we can confidently reflash no matter how badly we brick them. They'll definitely have a UART. They may have JTAG. We've got our own USB voice coming out.

##### **Geohot** [[00:32:59](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1979)]
So that'll be fun.

##### **Qazalin** [[00:33:04](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1984)]
Mm-hmm.

##### **Geohot** [[00:33:17](https://www.youtube.com/watch?v=5XHgivHDYPg&t=1997)]
How do we go about deleting more stuff in extra and external?

##### **Chenyu** [[00:33:26](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2006)]
I think there are still a lot of old stuff that are. So it's probably better to delete it.

##### **Geohot** [[00:33:31](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2011)]
I mean, yeah, feel free to delete. I don't know. I just went through and looked for old stuff.

##### **Geohot** [[00:33:37](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2017)]
And it's old stuff.

##### **Chenyu** [[00:33:39](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2019)]
It's like I searched Shape Tracker, and there are still 20 files. Oh, that's a good idea, yeah.

##### **Geohot** [[00:33:46](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2026)]
Anything that uses Shape Tracker, I'm sure we can just delete.

##### **Chenyu** [[00:33:48](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2028)]
Shape Tracker, lazy buffer, something like that.

##### **Geohot** [[00:33:51](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2031)]
Yeah. And we should delete everything. I also think we should start deleting. Like, I want to delete the. I want to delete the other LLM implementation. I want to get everything into. The MOE that I wrote for TinyGradApps LLM is like, it's the essence of MOE. If you read the one in there, it's so few lines. It's beautiful. TinyGradApps LLM now supports LLaMA. It supports Quen, and it supports Alma. Quen and Quen MOE.

##### **Chenyu** [[00:34:28](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2068)]
Yeah. Yeah.

##### **Geohot** [[00:34:29](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2069)]
So yeah, I know we still need the LLaMA for some of the multi-DPU stuff, not in LLM yet. But I think we can delete the Alma in example, and just use TinyGradApps LLM.

##### **Chenyu** [[00:34:44](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2084)]
OK.

##### **Geohot** [[00:34:46](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2086)]
I like that we have an LLM in there now, because I really think by the end of next year, instead of Beam, it's going to be like LLM equals 1, and it's going to use the LLM to. Yeah. Yeah. And then we can just run things and be like, oh, you aren't saturating all the warp. Here, let me try. I think we can even use a relatively small model for that. And it's the perfect. So what's made these new AI models good is it's called RLVR, Reinforcement Learning from Verifiable Rewards. So it could be pretty easy to fine tune a Quen free coder. Yeah. Yeah. On just like, well, we could fine tune it for a month on just sitting there with GPUs, frying stuff, and then up weighting all the traces where it eventually

##### **Geohot** [[00:35:43](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2143)]
gets high performance kernel. So instead of having heuristics.py,

##### **Geohot** [[00:35:52](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2152)]
we'll just have an LLM that one-shots it. And then the amount of search we do, is just how long we run that LLM for. Like if you wanted to search for, if you wanted the one shot, OK, great. Ask the LLM, hey, here's my kernel. Here's some information about it. Cool, what are the right optimizations? OK, see what you get with the one shot. See what you get with the three shot.

##### **Geohot** [[00:36:14](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2174)]
See what you get with the 10 shot. No, but yeah, it's so nice how we're not,

##### **Geohot** [[00:36:23](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2183)]
and it's not going to be like weird and finicky with stuff either. It's going to just be. Like coding, the language that we're

##### **Geohot** [[00:36:32](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2192)]
going to use to specify the optimizations is Python. Yeah, it's about that. Reinforcement learning over and over.

##### **Qazalin** [[00:36:53](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2213)]
Hey. Cool. Anything else for the meeting?

##### **Geohot** [[00:37:14](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2234)]
Not really. Merry Christmas. Happy holidays.

##### **Chenyu** [[00:37:19](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2239)]
Happy holidays. So for small updates, you can just update in the channel. And for everyone working on. Right. Wow code, try LLM. See, let's use this time to try something different.

##### **Geohot** [[00:37:37](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2257)]
Yeah, I like that. Cool, and that's it for this meeting.

##### **Chenyu** [[00:37:42](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2262)]
Thanks, everyone.

##### **Geohot** [[00:37:43](https://www.youtube.com/watch?v=5XHgivHDYPg&t=2263)]
See you next week. Bye.
