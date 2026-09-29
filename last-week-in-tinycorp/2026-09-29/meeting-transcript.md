# 2026-09-29 Meeting

### Meeting Agenda

**Time:** new meeting #39, 9/29 12pm Hong Kong time
- company update
- WMMA, AxisType, GROUP_REDUCE, UNROLL
- BACKEDGE, END, UNSHARD
- CI
- train gpt-oss
- hcq2, multi machine
- CALL INS
- bounties, Comma, RDNA


### Audio

[Youtube Link](https://www.youtube.com/watch?v=RRRxIw3c7K4)

### Highlights

- **[Company Update](#geohot-000007)**: AMD contract’s four milestones are done; need to ensure MLPerf submission is correct, reached out to Nvidia for the next contract, and AMD extension discussion focused on MI450/cloud and token interactivity curves.
- **[Move SGLang to tinygrad](#geohot-000250)**: After MLPerf, plan to move GLM/Kimi models currently hosted with SGLang over to tinygrad.
- **[Compiler Refactors](#chenyu-000801)**: Chenyu removed `GROUP_REDUCE` (now `LOCAL`), is working on removing `UNROLL` as an `UPCAST` reduction, and discussed WMMA/CALL and UNSHARD/multi-device representation.
- **[Tests, BACKEDGE, schedule2](#geohot-001443)**: Test suites refactored into null/runtime/device-specific; `Ops.BACKEDGE` added; `IF` and `RANGE` unified; `schedule2` simplifies variables as `PARAM`s with bind values.
- **[CI Status](#chrism-002141)**: CI passing on local Gitea, but queue/startup time is still slow; VMs are isolated except for cache server, and GPU runners in VMs are higher priority than Mac runners.
- **[GPT-OSS and MLPerf](#wozeparrot-003332)**: First sub-119 GPT-OSS run achieved via kernel tweaks and eval BS16; MLPerf logging changes needed, including dtype/comms logging for LLaMA and GPT-OSS.
- **[MLPerf Sprint Targets](#geohot-003856)**: Deadline is the 16th, but Geohot wants qualifying logs for all AMD milestones by end of sprint; targets include LLaMA under 90 minutes and qualifying GPT-OSS under 71.
- **[HCQ2 Updates](#nimlgen-003939)**: Fixing integrated USB GPU cache performance; multi-node GPT-OSS merged; JIT caching/pickled schedule saves minutes; OpenCL port is the last HCQ2 target.
- **[CALL/INS and Codegen](#qazalin-004744)**: BINARY renderer and ALLOC codegen merged; moving toward rendering CALLs inside kernels and outputting the whole model as one C program; assembly path being explored.
- **[GEMM MFU Gap](#qazalin-005308)**: AMD GEMM at ~40% MFU vs NVIDIA ~70%; needs better instruction scheduling and register allocation solver, and Geohot says it is not fundamental.
- **[x86/RDNA3 CALLs](#raine-005628)**: Raine is working on x86 instruction CALL bodies; Geohot wants hand-specified UOp implementations as the source of truth for instruction selection.
- **[Comma HCQ2 Issues](#chrism-005936)**: Comma reports USB GPU unplug hangs forever; need libusb error handling in HCQ2. Recovering in the same process after open failure was deemed unreasonable.
- **[Local LLM/Qwen](#geohot-010300)**: Qwen3.8-27B on 7900 XTX is fastest with tinygrad; after the AMD contract, plan to replace SGLang servers with tinygrad.
- **[Secret Project](#geohot-010614)**: Board shipping tomorrow; 116 GPUs available and trying to buy more; test by pulling eight GPUs from AMD2 for a board.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=0)]
Great. Welcome, everyone. Let's get started with company updates.

##### **Geohot** [[00:00:07](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=7)]
It looks like we finished all four milestones of the AMD contract. We have to make sure everything is actually submitted to MLPerf, but that's good. So I reached out to Nvidia to see if they want to give us the next contract.

##### **Geohot** [[00:00:27](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=27)]
You see, I've got to think about it from Nvidia's perspective, right? Is it worth $2 million to Nvidia to not have us have AMD beat them? I think it should be, right? I think if the right person at Nvidia was thinking about it, that's definitely worth $2 million and two boxes to them.

##### **Geohot** [[00:00:48](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=48)]
I reached out to AMD about extending the contract, and they followed up about MI450. They suggested their cloud partners, but I don't want cloud. So, you know, like, that seriously shows that they don't understand, you know, understand us, and we'll see if Nvidia understands us better.

##### **Geohot** [[00:01:13](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=73)]
Look, we can pull teeth and get another AMD contract. They're also not interested in MLPerf anymore, which kind of makes sense. What they're interested in is token interactivity curves.

##### **Geohot** [[00:01:30](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=90)]
SemiAnalysis has something called AgentEx, I think. The numbers that they're interested in are tokens per second per chip and tokens per second per user.

##### **Geohot** [[00:01:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=103)]
So, you can kind of, you know, you can trade those things off, those interactivity curves. So, that's fine as a target. But, yeah, no, if they want us to use cloud, Nvidia should. So, yeah, I got a reply from someone who's pretty high up at Nvidia. They wanted a meeting. I said no meeting, and I just wrote the thing up in an email. And we'll see if they're serious or not. But, yeah, I mean, if the right person at Nvidia actually understands what this is, it is absolutely worth $2 million to us to have us not work on AMD for the next six months.

##### **Geohot** [[00:02:15](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=135)]
It'll be good. It'll be good to get the Nvidia data center card. It's supported also. But otherwise, we should consider us working on AMD.

##### **Chenyu** [[00:02:25](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=145)]
I see. So, they want more of the inference benchmark, not so much for training?

##### **Geohot** [[00:02:32](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=152)]
They're thinking about next quarter. What sells things right now is tokens per second per chip and tokens per second per user. The more tokens per second per chip you can get while maintaining a basic level of interactivity, the better.

##### **Geohot** [[00:02:50](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=170)]
It's a different kind of benchmark, but it makes sense. We're interested in that too. Right now, our GLM and Kimi models are hosted with SGLang. We need to move that over to tinygrad; I think that's the next thing after MLPerf.

##### **Geohot** [[00:03:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=190)]
Yeah.

##### **Chenyu** [[00:03:12](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=192)]
Let's make sure we got our money and submit things correctly.

##### **Geohot** [[00:03:16](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=196)]
Yes. Yes. It's very important that we submit things correctly. I think also we should make sure that we write a nice statement for the press when the MLPerf stuff comes out. I think we can get some press around this.

##### **Chenyu** [[00:03:28](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=208)]
Yeah. You can write, I think, 300 letters of some marketing material.

##### **Geohot** [[00:03:33](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=213)]
Yeah. Yeah. Yeah. Just, you know, feed it to the best LLM and tell it to sound like a human. But yeah, no, I think that it's very exciting that we now actually are the state of the art at LLM training.

##### **Geohot** [[00:03:48](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=228)]
I mean, I think if we ported our stuff to NVIDIA, we would beat NVIDIA's time. I think our work is better. NVIDIA's time is mostly better because their GEMMs are better tuned, which we could also fix for AMD. A lot of people forget, you know,

##### **Geohot** [[00:04:07](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=247)]
just forget about the basics of what's actually going to be, what's actually going to matter. You know, people are excited about token interactivity curves now. But look, we're not going to be doing that. Like, how long is this token paradigm even going to stay around?

##### **Geohot** [[00:04:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=262)]
I think not that much. I think in five years, like, it kind of won't be a thing. I mean, some of this is just very hard to predict, right? Yeah, no, I think that, like, there are some definite things that we can predict, which are people are going to want more compute, more memory bandwidth, and more easy ways to use it.

##### **Geohot** [[00:04:49](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=289)]
So yeah, I don't know. I mean, like, maybe it stays around. But I think that, like, I don't know, maybe. I mean, maybe we do manage to, like, keep learning away from, I don't know. I mean, I guess I'm baffled at the large companies who think AI is a good idea.

##### **Geohot** [[00:05:14](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=314)]
What you really want as a company is your own fine-tuned model, trained on your company and source code. We want that too. I suspect a fine-tuned Qwen 2.5 7B would do a better job writing a lot of tinygrad code than frontier models.

##### **Geohot** [[00:05:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=343)]
So you know, it's about shipping those capabilities.

##### **Chenyu** [[00:05:47](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=347)]
Okay. We'll see.

##### **Geohot** [[00:05:49](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=349)]
We'll see. I don't think the current trend can continue. Like, the trend of models just getting bigger. AI has this amazing property where you can spend exponentially more money to get linear returns. And, like, that's what we've seen.

##### **Geohot** [[00:06:16](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=376)]
Okay. So, yeah. I don't know. We'll see. We'll see.

##### **Geohot** [[00:06:20](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=380)]
Maybe tokens will stick around. The fundamental need to use compute and memory bandwidth flexibly will still be here in five years. Things don't just disappear.

##### **Chenyu** [[00:06:47](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=407)]
Now it's hard to say what counts as a token. In multimodal models, people call an embedding a token too.

##### **Geohot** [[00:07:00](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=420)]
I just put multimodal Qwen in tinygrad. It's cool: a ViT embeds the image.

##### **Chenyu** [[00:07:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=430)]
So, everything is kind of embedding and everything is a neural net again. So, yes, we have token, but we also don't have token. So, I don't know.

##### **Geohot** [[00:07:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=438)]
Yeah. Yeah. Yeah. Sure. I guess as much as you call a token an embedding, yeah, it's not like embeddings are going to go anywhere. Like, the concept of an embedding is super fundamental.

##### **Chenyu** [[00:07:30](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=450)]
Yeah. It's just like a representation.

##### **Geohot** [[00:07:33](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=453)]
Yeah.

##### **Chenyu** [[00:07:34](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=454)]
Okay.

##### **Geohot** [[00:07:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=455)]
Oh, yeah. We'll see. We'll see where this ends up going.

##### **Chenyu** [[00:07:38](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=458)]
Great. We'll bet money. We'll have a very good year this year. Yeah.

##### **Geohot** [[00:07:45](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=465)]
We made money this year. I don't know what we want to put it on.

##### **Chenyu** [[00:07:54](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=474)]
Oh, what? Anyway, we can discuss like Hong Kong.

##### **Geohot** [[00:07:58](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=478)]
All right. Cool. Okay.

##### **Chenyu** [[00:08:01](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=481)]
Okay. Let's move on to actual items. So, first one is mine. I removed GROUP_REDUCE; it's just LOCAL now. I'm also working on removing UNROLL. That will be an UPCAST reduction.

##### **Geohot** [[00:08:20](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=500)]
Great.

##### **Chenyu** [[00:08:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=502)]
We briefly discussed WMMA. This might be related to the CALL/INS work, depending on whether we want to put a shape on the instruction. One way is to give WMMA the shape of that instruction.

##### **Geohot** [[00:08:45](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=525)]
Well, do you mean the complete shape of the entire matrix or the shape of the... The

##### **Chenyu** [[00:08:51](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=531)]
shape of the instruction.

##### **Geohot** [[00:08:55](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=535)]
Yeah. That should be right. But you mean just the shape from the view of a single thread?

##### **Chenyu** [[00:09:03](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=543)]
We can do that from the view of a warp.

##### **Geohot** [[00:09:09](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=549)]
Well, if we want to do it from the view of the warp, it's the same problem basically as multi.

##### **Chenyu** [[00:09:14](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=554)]
Yes, I understand that part. That's why I started reading the new UNSHARD work and found bugs in the current implementation. I want to handle it similarly to multi-device, because gathering from different lanes is essentially the same problem.

##### **Geohot** [[00:09:39](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=579)]
Yes. Yeah.

##### **Chenyu** [[00:09:41](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=581)]
For WMMA, it's the same thing. We can discuss it more in Hong Kong because it involves several people. The idea of writing it as a CALL is similar to other instructions: we could remove Ops.WMMA and use a CALL instead. Modeling it across a warp makes sense, but then it resembles the multi-device problem. That's my current understanding.

##### **Geohot** [[00:10:09](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=609)]
Yeah. There's a bunch of bits of subtlety to this. So, like one of the problems that I'm struggling with now is, so I've added the range to the buffers. And you can imagine that same range for the buffers on the register, right? Like the multi device has a device range across the buffer. The registers have a warp.

##### **Geohot** [[00:10:31](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=631)]
But part of the problem is then putting that into a call. Because if you put that into a call, what happens with that range? Like you can't just put a single register view into the call. Because once you're in the call, you don't have access to that range anymore. And the calls can't interact.

##### **Chenyu** [[00:10:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=656)]
If you look at the current TensorCore code, the WMMA argument represents something like that. It also represents what you just described, with something like an upcast axis.

##### **Geohot** [[00:11:20](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=680)]
What we're doing now depends on how the loads were set up.

##### **Geohot** [[00:11:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=703)]
Right, like things have to be on their correct thread in order for WMMA to produce the results. Yeah.

##### **Geohot** [[00:11:51](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=711)]
So, like, I don't know, I've been struggling with this. And maybe this is something we should just we should all discuss in Hong Kong because I haven't figured out like a representation that that puts the range into the call correctly.

##### **Geohot** [[00:12:08](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=728)]
That's simple.

##### **Qazalin** [[00:12:13](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=733)]
Sure.

##### **Geohot** [[00:12:14](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=734)]
I don't have anything else. I think it's the same problem. If you're interested, I posted the changes in fast_tinygrad. There are a few new OptOps in there, although I think there's really just one.

##### **Geohot** [[00:12:32](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=752)]
Also just a few, like it doesn't do split reduce on CPU anymore. If you're interested, it gets all yellow and green on Torch compared with LLVM.

##### **Chenyu** [[00:12:44](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=764)]
let's see. What I posted. With these changes.

##### **Geohot** [[00:12:52](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=772)]
Yeah, yeah. With these changes.

##### **Chenyu** [[00:12:55](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=775)]
I think I'll take a look.

##### **Geohot** [[00:12:57](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=777)]
Yeah, I don't know if you're interested in any of that. But it's just like more kind of beam fix ups.

##### **Chenyu** [[00:13:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=784)]
It's possible that some of these are hard to test. It's possible that some of the refactors silently removed part of the search space. Yeah. I would take a look.

##### **Geohot** [[00:13:17](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=797)]
Yeah. I mean, so I broke the, when I did that variable refactor, we have like no tests for variables and beam. I broke it. I added a test, but I don't know how great it is. But yeah,

##### **Geohot** [[00:13:32](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=812)]
Our BEAM search is getting better, though.

##### **Chenyu** [[00:13:34](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=814)]
Yeah. I'm working on this. Oh, yeah. Previously we had about seven different actions and were limiting the search too much. My recent changes made the search space more robust and hopefully improved the results.

##### **Geohot** [[00:13:57](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=837)]
Yeah.

##### **Chenyu** [[00:13:59](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=839)]
Cool. Yeah. I would take a look at this. I'm cleaning this up anyway.

##### **Geohot** [[00:14:05](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=845)]
I'm looking forward to TensorCore no longer being a separate optimization action.

##### **Geohot** [[00:14:24](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=864)]
It's really instruction selection for a particular shape, so we need to think through that representation.

##### **Chenyu** [[00:14:29](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=869)]
We'll know more after the assembly work improves.

##### **Geohot** [[00:14:34](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=874)]
I agree.

##### **Chenyu** [[00:14:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=875)]
That's my update. We can move on to yours.

##### **Geohot** [[00:14:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=883)]
Yeah. So I did. I did a bunch of test refactors. That was a decent chunk of my week.

##### **Geohot** [[00:14:52](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=892)]
I got rid of test/unit; it didn't make much sense. We now have three kinds of tests: test/null, which doesn't require a device; test/runtime, which should pass on every runtime; and device-specific AMD and NVIDIA tests.

##### **Geohot** [[00:15:16](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=916)]
I also got rid of test/opt. We can keep test/external for now, but test/extra should be integrated into the other suites and test/speed should go under external tests.

##### **Geohot** [[00:15:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=935)]
I also worked on BACKEDGE. We had been overloading END to represent a conditional break. I added a separate Ops.BACKEDGE. Its first source is the body, its second is the RANGE, and it also has a termination condition. It is basically a do-while loop, and I think it is cleaner.

##### **Geohot** [[00:16:03](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=963)]
We should also change the PTX and LLVM backends. They currently use the renderer to lower these constructs; doing that earlier in the graph would be cleaner.

##### **Chenyu** [[00:16:19](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=979)]
Lowering and rendering do a lot of strange things, including a pre-match step for instruction selection and rewrites.

##### **Geohot** [[00:16:37](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=997)]
Yeah. I mean, yes, that's bad. But this one I'm talking about is even worse than that. So we have, like, if you look in, like, PTX, we have, like, for range and end.

##### **Geohot** [[00:16:53](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1013)]
Like, these things are really complicated. And we can just refactor that to back edge. There shouldn't be an END there anymore; it should be a BACKEDGE. If you look at PTX's END rendering, it performs an ADD and a CMPLT. Those operations should be lowered into the graph instead.

##### **Geohot** [[00:17:15](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1035)]
The ADD and CMPLT should be handled by normal graph processing.

##### **Chenyu** [[00:17:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1042)]
Okay.

##### **Geohot** [[00:17:23](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1043)]
We also have IF. If you look at Ops.IF and Ops.RANGE, they're essentially identical. How are IF and RANGE identical? An IF executes zero times when its condition is zero and once when it is one. A RANGE with that bound does the same thing. So I unified them.

##### **Geohot** [[00:17:52](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1072)]
I also spent a lot of time on schedule2, a replacement for the scheduler. I've been simplifying it as I go. For example, I removed the BUFFER/STORE/AFTER mechanism for variables. Variables are now PARAMs with a bind value.

##### **Geohot** [[00:18:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1102)]
Simplified a bunch of things. That's really the correct way to do it.

##### **Geohot** [[00:18:30](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1110)]
The struggle has been with END and UNSHARD. UNSHARD is essentially END, except UNSHARD has an arg that says where to insert the axis, while END always inserts it at the leading position. I have an AI branch with this refactor, but pushing END through movement ops becomes difficult. If a PERMUTE moves that leading axis, there is no way to move the PERMUTE above END.

##### **Geohot** [[00:19:12](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1152)]
That's one thing to decide. I've also added ranges to BUFFER, which makes sense to me; BUFFER and UNSHARD now end the range. I don't yet know how this should interact with CALLs. Can you pass that range into a CALL? If you pass it naively, it becomes a PARAM.

##### **Geohot** [[00:19:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1175)]
But you can't END a PARAM. A CALL could operate on one device or on all devices in the range at once. An all-reduce is a synchronization barrier. If the range is outside the CALL, with END after it, then the CALL is effectively a barrier across devices. I don't know the right representation yet, but the core idea is that UNSHARD is END.

##### **Geohot** [[00:20:16](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1216)]
You END the device range to get the larger virtual tensor, then push END down through the graph. We could use the same approach for a warp and what TileLang calls a fragment.

##### **Geohot** [[00:20:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1235)]
That's most of my work. I've also been adding vision to Qwen. It works; it can sort of play Pokemon.

##### **Chrism** [[00:20:46](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1246)]
What do you mean by "kind of plays Pokemon"?

##### **Geohot** [[00:20:47](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1247)]
I wrote a program for it this weekend.

##### **Chenyu** [[00:20:53](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1253)]
I saw your demo, but does it really play?

##### **Geohot** [[00:20:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1256)]
Astra does. Oh, Astra is really good.

##### **Chenyu** [[00:21:00](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1260)]
I can't believe Astra can finish it.

##### **Geohot** [[00:21:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1264)]
I don't know if it can finish the game; no one has the money to find out. It can reach Viridian Forest. MiMo can't leave the starting room. GLM-4.7-Flash can. Qwen also struggles to leave the starting room; it thinks it's in Oak's lab.

##### **Geohot** [[00:21:23](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1283)]
But I don't know if that's because of bugs or because of other stuff.

##### **Chenyu** [[00:21:32](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1292)]
Yeah. Cool. Good stuff. OK, moving on. Next we have CI.

##### **Chrism** [[00:21:41](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1301)]
Yeah. So I have a PR open where the CI all ran and passed on our local machines. Right now, I mean, if you look at it, it looks like it ran fast. But the thing I need to solve is the time to queue the jobs is kind of long.

##### **Chrism** [[00:21:59](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1319)]
So I'm going to figure out how to make that faster. I think just spinning up the VMs is a little bit slow. And there's probably all sorts of stuff that I can do to make that a little faster. So I'll just try to look into benchmarking that.

##### **Chrism** [[00:22:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1330)]
It's all running on Gitea and has been passing reliably. We still download some things from GitHub, so we aren't fully insulated from GitHub outages.

##### **Geohot** [[00:22:28](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1348)]
Are these VMs isolated from our internal network?

##### **Chrism** [[00:22:33](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1353)]
Yes. So they can access one machine, which is running the caching server. And they should only be able to access that machine. That's the intent.

##### **Geohot** [[00:22:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1363)]
Yeah, throw an LLM on red teaming this.

##### **Chrism** [[00:22:47](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1367)]
Yeah, I did. I'll do it some more, though. Astra refused. It said the red-teaming request was cyber-related.

##### **Geohot** [[00:22:59](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1379)]
Use the local GLM-4.7-Flash. It's actually kind of bad at this.

##### **Chrism** [[00:23:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1384)]
OK, all right. I'll try that.

##### **Geohot** [[00:23:06](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1386)]
Even if you get past Astra's guardrails, its cybersecurity capabilities have been heavily restricted.

##### **Chrism** [[00:23:13](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1393)]
Yeah, yeah. OK. Yeah, I'll give that a shot. Yeah, I already asked GLM a little bit, but I'll try to get it to push a little harder.

##### **Chrism** [[00:23:24](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1404)]
Yeah, anyway, so that's good. If you look at the timings, you'll see that it's kind of, you know, it's kind of a little bit more than what it was before. Yeah, it's not. There's some things that are slower, there's some things that are faster. So the stuff that's faster is obviously like downloading stuff from the internet. Anything that's heavily dependent on downloading stuff from the internet, like test LLM, is much faster because it's all cached.

##### **Chrism** [[00:23:44](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1424)]
And then on the flip side, there's stuff that's, so for instance, like I think, sorry, yeah, the one that's dev equals CPU clang. That, since it's mostly just doing CPU work, is slightly slower.

##### **Geohot** [[00:24:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1444)]
Test LLM is not that fast.

##### **Chrism** [[00:24:11](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1451)]
Wait, isn't this... OK, maybe I'm not comparing it to the right thing.

##### **Geohot** [[00:24:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1458)]
I don't know what it is in GitHub, but I would expect that download, if that's cached, to be a lot faster.

##### **Chrism** [[00:24:31](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1471)]
Yeah, that is slow. OK, the previous time I ran it, that was 200. So I don't know. I'll have to look into that.

##### **Geohot** [[00:24:42](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1482)]
I don't even know. It doesn't even show the downloads. Oh, it's all just the cache. Yeah, I mean, the GitHub one is faster right now. So the GitHub one, that one's getting 50 megs a second. The GitHub one is getting... 100 and...

##### **Geohot** [[00:25:02](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1502)]
But I would expect that to be almost a gigabyte, right? Almost gigabyte.

##### **Chrism** [[00:25:07](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1507)]
It should be, yes. I've seen that be way higher. I don't know. I need to look at that. Because I feel like the previous run, that was way faster. But I'll have to look at that.

##### **Chrism** [[00:25:23](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1523)]
It's possible... So it's possible the Hugging Face caching is kind of annoying. It's possible I screwed something up there. It's definitely possible I messed something up with the Hugging Face cache.

##### **Chrism** [[00:25:36](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1536)]
Like, you have to go through multiple layers and cache the right thing?

##### **Geohot** [[00:25:40](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1540)]
Yeah, I mean, in general, we should just be monitoring our egress and making sure that we aren't spamming the internet. Yeah, for sure. But cool. Glad it's local. And yeah, the times look better.

##### **Chrism** [[00:25:57](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1557)]
They're not universally better.

##### **Geohot** [[00:25:59](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1559)]
This is on... you gave it four cores per job?

##### **Chrism** [[00:26:02](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1562)]
Yep.

##### **Geohot** [[00:26:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1564)]
And that's... you put... how many runners on the machine?

##### **Chrism** [[00:26:07](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1567)]
32, across multiple machines. The more jobs run simultaneously, the slower each one gets.

##### **Geohot** [[00:26:24](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1584)]
Yeah, I mean, I think this is true about namespace, too. Yeah.

##### **Chrism** [[00:26:27](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1587)]
That might be true. I'm not sure.

##### **Geohot** [[00:26:29](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1589)]
I've definitely seen namespace variance be...

##### **Chrism** [[00:26:32](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1592)]
That's definitely true here too: concurrent jobs slow each other down.

##### **Geohot** [[00:26:40](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1600)]
That makes sense.

##### **Chrism** [[00:26:42](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1602)]
We should also consider moving our Mac runners. The GitHub Mac runners are very slow, so that could make a big difference.

##### **Geohot** [[00:26:55](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1615)]
Yeah. I mean, we gotta... how are we gonna get around the... Are you looking at the custom kernel thing at all? So we can run more VMs?

##### **Chrism** [[00:27:02](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1622)]
Oh, yeah, yeah, yeah. Yeah, I can look at that.

##### **Geohot** [[00:27:05](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1625)]
I don't know how much time we should spend on this, though.

##### **Chrism** [[00:27:08](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1628)]
Yeah. So, if we're just gonna run... I'll take a look at it. But I think... Like, the jobs are so much faster that we could probably consolidate some of them. And still have them run within this timeframe. And, you know, we have however many Macs. Like, it probably is the same.

##### **Geohot** [[00:27:27](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1647)]
That would be cool. Part of my test refactor was to simplify this.

##### **Chrism** [[00:27:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1655)]
Oh, for sure. Yeah. I mean, this is the dream, is to be able to say that, like, you just have, like, Linux and that's, you know, one big matrix.

##### **Geohot** [[00:27:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1663)]
Yes, the runtime tests could fit into one Linux matrix.

##### **Chrism** [[00:27:49](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1669)]
Yeah. Yeah. Anyway, that was the big thing that I've been working on. Yeah. Oh, also, everything's on 10 gig now. Which definitely did make a difference for the download speeds for that stuff.

##### **Chrism** [[00:28:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1684)]
Yeah, you know what I probably... I bet happened? Is that probably, like, all the download jobs got scheduled on one machine. And then they're all bottlenecked by that. Yeah.

##### **Chrism** [[00:28:12](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1692)]
I'll look into that. If download jobs are spread across machines, it should help a lot.

##### **Geohot** [[00:28:21](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1701)]
It's not that slow. Like, it's not like that time is totally unusable.

##### **Chrism** [[00:28:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1706)]
Yeah, yeah, that's true. That's true. It should be faster, though. I'm not sure why it's not faster. Yeah. Yeah. Anyway, anyway. I'll look into that later.

##### **Geohot** [[00:28:38](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1718)]
I think GARM startup time matters more than maximum throughput.

##### **Chrism** [[00:28:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1723)]
For sure. Yeah. It looked like it was like 30 seconds or something like that.

##### **Geohot** [[00:28:46](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1726)]
Yeah. Yeah, I'll post in... Is there a way that we can see the GARM? I run the... I see it.

##### **Chrism** [[00:28:54](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1734)]
So, yeah. So right now I only enable the Cloudflare tunnel for the webhook endpoint, but I can enable it for the whole web UI.

##### **Geohot** [[00:29:03](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1743)]
Yeah, if we're confident that that's...

##### **Chrism** [[00:29:07](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1747)]
I have not audited that code. So I have

##### **Geohot** [[00:29:11](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1751)]
no idea. Let's audit it a little. But yeah, I think that would definitely be cool to have.

##### **Chrism** [[00:29:17](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1757)]
If we don't expose it through Cloudflare, you can use a SOCKS proxy or Tailscale to reach it on tinygateway2.

##### **Geohot** [[00:29:30](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1770)]
I like making this accessible publicly.

##### **Chrism** [[00:29:34](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1774)]
Yeah, it's kind of cool. I mean, so right now it's password protected. So like it'll just... If you just visit it, it's like just a... It's just like, here's the login screen.

##### **Geohot** [[00:29:47](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1787)]
We can keep it password protected, but make it easy to access it.

##### **Chrism** [[00:29:52](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1792)]
Yeah, yeah. Yeah, no, I'm just kidding. I mean, I agree. I think it's nicer to be able to just see it.

##### **Geohot** [[00:29:57](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1797)]
I think stats.tinygrad.win will become more important as we test single-GPU performance. I'm already doing a lot for beam regressions in a way that I wasn't.

##### **Chrism** [[00:30:09](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1809)]
Another major task is getting the GPU runners working in VMs. That should reduce the current resource leakage.

##### **Geohot** [[00:30:23](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1823)]
That's more important. The Mac runners aren't a priority right now.

##### **Chrism** [[00:30:29](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1829)]
Okay. Yeah, I won't worry about that.

##### **Geohot** [[00:30:33](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1833)]
Well, we'll get there, but GPUs are higher priority.

##### **Chrism** [[00:30:36](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1836)]
Yeah, yeah, for sure. I may have to write my own GARM provider for that. I was hoping Incus would provide an easy way to do it.

##### **Chenyu** [[00:30:46](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1846)]
Doesn't Incus have a way to pool the GPUs?

##### **Chrism** [[00:30:49](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1849)]
No, no, it does. But it doesn't have a nice way to be like, oh, like, here's my pool of GPUs. Yeah. Right. So like, you know, oh, this machine has like six, you know, 3090s in it and just, you know, spin me up a VM with a 3090 in it. I see. There's no nice way to do that.

##### **Geohot** [[00:31:03](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1863)]
Yeah.

##### **Chrism** [[00:31:06](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1866)]
Anyway, that's not a lot of work.

##### **Chrism** [[00:31:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1870)]
The other thing I want to do is put the BMCs on their own network and decide whether it needs internet access. That depends on what Wozeparrot wants for provisioning and where it runs. Two separate networks would keep the BMCs isolated.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1896)]
Agreed. Yeah.

##### **Chrism** [[00:31:41](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1901)]
Oh, and I looked at the dev equals thing. The easiest way to do that GFX 1201 thing, like if you just want to have a look at the arch, is just to have like a lookup table between the...

##### **Chrism** [[00:31:54](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1914)]
Like the arch numbers and the product IDs. Because the alternative is that you have to open every single GPU, like every single device, and then check which arch it is and then say, oh, we don't want that. Oh, we want this. Which is not really how the code is architected there right now.

##### **Geohot** [[00:32:14](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1934)]
I'll leave that to you. Whatever you want to do for it. I'm fine with that lookup table.

##### **Chrism** [[00:32:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1938)]
Okay.

##### **Geohot** [[00:32:20](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1940)]
Yeah, if you have one. You see what I mean about the architecture numbers. I mean, I can see the analogy about how it's basically the same thing as AMD versus NV.

##### **Chrism** [[00:32:27](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1947)]
Yeah, I do see that. Yeah, I mean, I can see the argument for either one. But yeah, it just feels like a filter on... I don't know. Like the left side of the plus to me feels like it's sort of specifying runtime information. And then the right side of the plus seems like it's specifying compile information.

##### **Geohot** [[00:32:53](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1973)]
But no way. I mean, obviously, the right side of the plus is specifying whether you bind to an AMD GPU or an NVIDIA GPU, right? Yeah, that's true. Yeah, you're right.

##### **Geohot** [[00:33:14](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1994)]
Let's do that and get HCQ2 back on CI.

##### **Chenyu** [[00:33:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=1998)]
Sounds good.

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2004)]
Okay, yeah, 10 years out. Anything else? No,

##### **Chrism** [[00:33:29](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2009)]
I think that's it.

##### **Geohot** [[00:33:30](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2010)]
All right, GPT-OSS.

##### **Wozeparrot** [[00:33:32](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2012)]
So we have our first sub 119 run. Sweet. And then this was mainly just a combination of small kernel tweaks and then switching eval to BS16. Nice. To match our training BS.

##### **Wozeparrot** [[00:33:50](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2030)]
That's eval startup time as well.

##### **Geohot** [[00:33:53](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2033)]
You should be able to save at least another 30 seconds with SCACHE=2. Even ten seconds would help. Let's make sure the time we submit to MLPerf is 1:58.

##### **Wozeparrot** [[00:34:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2050)]
This week I'll focus on submissions and logging changes. The new MLPerf submission requirements were released over the weekend.

##### **Geohot** [[00:34:24](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2064)]
All the new stuff about how to submit.

##### **Wozeparrot** [[00:34:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2066)]
Yeah. Got it. There's some logging changes, we now have to log some D type stuff, some comms, like what our like lowest D type is. They tried this last year and had us add it retroactively.

##### **Wozeparrot** [[00:34:41](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2081)]
Now we have to log it fully. I need to add that to the LLaMA logger, and GPT-OSS doesn't have logging yet, so I need to add it there too. Then we should be ready to start the runs.

##### **Geohot** [[00:34:55](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2095)]
The machines are yours; let's run.

##### **Wozeparrot** [[00:35:01](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2101)]
Is LLaMA ready to run? And is multi-machine GPT-OSS ready? I saw a lot of testing over the weekend.

##### **Geohot** [[00:35:13](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2113)]
LLaMA is ready on my side.

##### **Wozeparrot** [[00:35:15](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2115)]
OK. It's still the same branch?

##### **Geohot** [[00:35:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2118)]
Branch.

##### **Wozeparrot** [[00:35:19](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2119)]
OK.

##### **Geohot** [[00:35:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2122)]
I'll share the configuration for multi-machine GPT-OSS.

##### **Wozeparrot** [[00:35:28](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2128)]
Yes. If you could just post something with a branch, we can just run.

##### **Geohot** [[00:35:37](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2137)]
It would be great to get a 66-minute two-machine run.

##### **Nimlgen** [[00:35:46](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2146)]
There is still a lot to run.

##### **Geohot** [[00:35:53](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2153)]
Yeah, okay. I'll try. Well, let's...

##### **Geohot** [[00:35:59](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2159)]
Let's... You know what? Let's save that for next sprint. Let's get stuff submitted. Let's get stuff logged and ready, even if it's not 66. I think we can save that for next sprint. But something that's qualifying under 71.

##### **Geohot** [[00:36:17](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2177)]
We want a sub-1-hour-41-minute LLaMA run. What about two-machine LLaMA?

##### **Wozeparrot** [[00:36:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2186)]
This was... I forgot what our target exactly was.

##### **Nimlgen** [[00:36:32](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2192)]
We don't have a specific target, but it should be ready and it's in master.

##### **Geohot** [[00:36:41](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2201)]
Two-machine LLaMA, yes. Yeah, let's try to get all of these things. Let's try to get the logging done for all these things this week.

##### **Chrism** [[00:36:59](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2219)]
Yeah.

##### **Geohot** [[00:36:59](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2219)]
Just so we know we're good. Yeah, well, you got the machines to yourself.

##### **Nimlgen** [[00:37:05](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2225)]
Yeah.

##### **Geohot** [[00:37:08](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2228)]
What's the best time we have for two-machine LLaMA? Hold on, I remember you shared something that was 1 hour, 30 minutes.

##### **Nimlgen** [[00:37:20](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2240)]
Yesterday I upstreamed some RDMA fixes, so it might be faster without any other changes. I haven't tested it yet.

##### **Geohot** [[00:37:37](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2257)]
If we could do less than 60 minutes, that'd be great.

##### **Nimlgen** [[00:37:48](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2268)]
Most of the GPT-OSS fixes hid latency, or rather, idle time. And I'm not sure the same approach works for LLaMA.

##### **Qazalin** [[00:38:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2290)]
For LLaMA, I would also have to update the branch.

##### **Geohot** [[00:38:23](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2303)]
don't know. Let's just go with... Okay, you know what? Let's just get something logged this week. Let's say under 90.

##### **Wozeparrot** [[00:38:32](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2312)]
Yeah.

##### **Geohot** [[00:38:34](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2314)]
Let's log a run under 90 minutes, and next sprint we'll have time to improve it. Actually, no. We might have a little bit of time to play with this to kind of go faster. But, yeah. So let's just make sure that we have a lot of time. Let's make the targets.

##### **Geohot** [[00:38:52](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2332)]
So pretty much anything.

##### **Wozeparrot** [[00:38:54](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2334)]
Is the 16th?

##### **Geohot** [[00:38:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2336)]
The deadline is the 16th, but I don't want to cut it close. I want qualifying logs for all AMD milestones by the end of this sprint. Okay. Okay.

##### **Geohot** [[00:39:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2358)]
Cool. Anything else on GPT-OSS?

##### **Chenyu** [[00:39:24](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2364)]
Nope.

##### **Geohot** [[00:39:29](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2369)]
Okay. Let's move on to HCQ2. Did you see...

##### **Nimlgen** [[00:39:39](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2379)]
Yeah, I'm fixing that. But... I'm fixing the integrated USB GPU performance. It isn't hitting the cache, which is what I was looking at.

##### **Nimlgen** [[00:39:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2396)]
So, yeah. Not much else for HCQ2. I did the multi-node GPT-OSS run and started merging the parts that look good into master.

##### **Nimlgen** [[00:40:15](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2415)]
And yeah, and yeah, I also have been fixing some some segfaults we had in our CI. I think it looks better now. I haven't seen segfaults since this week.

##### **Geohot** [[00:40:34](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2434)]
What were the causes?

##### **Nimlgen** [[00:40:37](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2437)]
It was the linker in the CPU. If the library was allocated far enough away, between two and four gigabytes, we jumped into garbage because we handled the relocation incorrectly.

##### **Nimlgen** [[00:40:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2456)]
Because we treat the relocation wrong.

##### **Geohot** [[00:41:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2464)]
I don't fully understand that.

##### **Chrism** [[00:41:09](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2469)]
The 64-bit jumped, right? Like, if your jump is too long?

##### **Nimlgen** [[00:41:15](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2475)]
No, it's... Oh.

##### **Geohot** [[00:41:19](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2479)]
I've seen that before.

##### **Nimlgen** [[00:41:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2482)]
Not this way.

##### **Geohot** [[00:41:25](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2485)]
This commit?

##### **Nimlgen** [[00:41:27](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2487)]
Yeah, this...

##### **Geohot** [[00:41:29](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2489)]
Oh, I see. Some ELF issue. Cool. Great work getting the 71-minute time. I owe you a bonus.

##### **Geohot** [[00:41:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2516)]
I'm happy with how this is going. There are still cleanups to do; we're spending a lot of time in HCQ2 rewrites that could be simplified.

##### **Nimlgen** [[00:42:09](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2529)]
We can discuss it in Hong Kong, but I wish we had the new multi-device model; HCQ2 uses multi-device now too.

##### **Geohot** [[00:42:21](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2541)]
Yeah, we're going to have a lot of conversations about the new multi-device model. I wish we had it too, but I don't know exactly how we want to express things. There are a lot of different angles to consider, and we should make sure we get this right.

##### **Nimlgen** [[00:42:40](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2560)]
For multi-node GPT-OSS I also used JIT caching: I pickled the entire schedule. It saves several minutes, and it complies with MLPerf rules because it doesn't touch the data.

##### **Geohot** [[00:43:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2584)]
If you have code for that, great. The SCACHE=2 change was only about three lines, but pickling the entire schedule is even better if it's easy to do.

##### **Nimlgen** [[00:43:16](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2596)]
Yeah, it's almost the same thing we do for OpenPilot. Yeah. So yeah.

##### **Geohot** [[00:43:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2602)]
Yeah, I mean, we have to think about... Hopefully now the JIT can kind of just kind of like fall away and, you know, this stuff's all easy to think about now.

##### **Chenyu** [[00:43:33](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2613)]
Cool.

##### **Geohot** [[00:43:38](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2618)]
Anything else?

##### **Nimlgen** [[00:43:41](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2621)]
No. This week I have OpenCL left to port to HCQ2. That's the last one. I'll also merge the multi-node GPT-OSS changes and the JIT cache into master.

##### **Geohot** [[00:43:55](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2635)]
Great. Yeah, hopefully the renderable call and renderable binary will help you out. Eventually HCQ2 should be able to output a standalone C program for something like OpenCL.

##### **Geohot** [[00:44:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2658)]
That's what I'm getting at. Is Metal done? Do you have one of the Stranger Ones done?

##### **Nimlgen** [[00:44:23](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2663)]
Yeah. CUDA and Metal.

##### **Geohot** [[00:44:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2666)]
CUDA and Metal are done. Let me read this code. Um... Okay, the CUDA queue and allocator. I didn't read this. This is great.

##### **Geohot** [[00:44:44](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2684)]
What is this `.h` field that gets set?

##### **Nimlgen** [[00:45:03](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2703)]
It orders the calls. I use that handle as the return value and add an AFTER later, so the calls are ordered correctly.

##### **Geohot** [[00:45:19](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2719)]
Yeah, I see. I see this, like, property stream thing that's reading it. Oh, I see what you're doing.

##### **Geohot** [[00:45:38](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2738)]
Yeah, that's fine. We can figure out if there's a better way to do that, but I see what it's doing. Either way, this is great. This is exactly how we want to think about things: being totally abstracted from the actual execution.

##### **Geohot** [[00:46:02](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2762)]
The longer we can wait before we ever actually open a device, the better. Opening a device and touching hardware is a horrifying thing, and we want to wait as long as possible. But yeah.

##### **Nimlgen** [[00:46:17](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2777)]
Another blocker in HCQ2 is that, to know the device configuration, we still have to open it during scheduling. We can discuss this later.

##### **Geohot** [[00:46:36](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2796)]
I mean, we should think about how to basically better abstract that, right? Like, it's not like you're never going to get around completely doing it.

##### **Geohot** [[00:46:46](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2806)]
Maybe you don't have to. This might be like the `DEV=` work we discussed before: keep a table specifying device configurations without having to open them. We could build that table once from the devices. Whatever we choose, the important thing is to isolate information gathering to one small part of the code, which generates a class from the device information.

##### **Geohot** [[00:47:29](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2849)]
Yeah, that's it for me.

##### **Chenyu** [[00:47:31](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2851)]
Cool.

##### **Geohot** [[00:47:40](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2860)]
Okay, let's do CALL/INS.

##### **Qazalin** [[00:47:44](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2864)]
Last week I merged some cleanups. We now have BINARY support in the renderer and ALLOC support in codegen. ALLOC mainly cleaned up our DSL. This diff in our AMD kernels removes handwritten slots and Kimi-written slots.

##### **Geohot** [[00:48:09](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2889)]
I wrote that myself. Oh, not in the kernels, I didn't, but in the CALL layer.

##### **Qazalin** [[00:48:12](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2892)]
I'm sure you didn't. There were random slots there; I don't know what those were.

##### **Qazalin** [[00:48:16](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2896)]
The random slots are cleaned up. We're moving toward rendering CALLs inside kernels, then outputting the whole model as one C program. Imagine compiling EfficientNet using only tinygrad.

##### **Qazalin** [[00:48:42](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2922)]
So that's what I've been working on. I have the PR almost done. The opt-ops are really annoying. I'm going through, like, figuring out the opts. And also, I want to support it on other devices. But

##### **Geohot** [[00:48:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2936)]
why does this have to do with opt-ops? I still don't understand.

##### **Qazalin** [[00:48:58](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2938)]
It has to do with opt-ops because, like, some things... Like, imagine how do you want to do a group reduce?

##### **Geohot** [[00:49:06](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2946)]
Why does rendering calls have anything to do with opt-ops?

##### **Qazalin** [[00:49:11](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2951)]
Well, it has to apply some optimization. It has to apply optimization on the calls, too, right?

##### **Geohot** [[00:49:16](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2956)]
Don't worry about that.

##### **Qazalin** [[00:49:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2958)]
So I just said apply opt to null? Don't apply any opts to call?

##### **Geohot** [[00:49:23](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2963)]
No, you're using the normal Codegen path. It should handle that, right?

##### **Qazalin** [[00:49:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2966)]
It doesn't.

##### **Geohot** [[00:49:28](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2968)]
Why not?

##### **Qazalin** [[00:49:28](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2968)]
Some cases fail. I could merge it now if we disallow OptOps in CALLs, but I would rather understand the failure.

##### **Geohot** [[00:49:44](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2984)]
That's probably fine, but I still don't understand why the Codegen pipeline doesn't work.

##### **Qazalin** [[00:49:52](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2992)]
I don't understand it either.

##### **Geohot** [[00:49:54](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2994)]
We should figure this out.

##### **Qazalin** [[00:49:55](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2995)]
Yeah.

##### **Geohot** [[00:49:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=2996)]
I wouldn't treat it as an OptOps issue. It sounds like the CALL rendering itself is done, and the failure lies elsewhere.

##### **Qazalin** [[00:50:19](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3019)]
Yes, rendering the CALL is done. The problem is in the later lowering path.

##### **Geohot** [[00:50:25](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3025)]
You have a separate `pm_lower_calls`. Why doesn't it use the same Codegen path as the other kernels?

##### **Qazalin** [[00:50:42](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3042)]
Calling the same Codegen code? Yes. It's basically lowering the same UOps.

##### **Geohot** [[00:50:46](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3046)]
You also have prerequisites you can merge separately, like source without body, and use them where needed.

##### **Qazalin** [[00:50:53](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3053)]
Yes, source without body. This morning I merged backward slicing without entering CALLs. I want that to become the default generally: we don't want to enter CALL bodies. We should also remove entering CALLs from GraphRewrite and use the self-calling PatternMatcher that the scheduler already uses.

##### **Geohot** [[00:51:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3086)]
GraphRewrite should only operate within a single scope. UOps inside a CALL body don't have the same meaning as UOps outside it. We don't want a GraphRewrite to span both scopes.

##### **Geohot** [[00:51:46](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3106)]
That sounds like a good change.

##### **Qazalin** [[00:51:48](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3108)]
that and then we can start working on assembly.

##### **Qazalin** [[00:51:52](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3112)]
I had Codex write a version of the assembly work to see how it would look. This is a GEMM written in RDNA3 assembly. Each `S_ADD_U32`, for example, implements that RDNA3 instruction in C. `SCC` is represented like a register. This is transpilation, or lifting assembly into a C program. At the end there's a for loop,

##### **Qazalin** [[00:52:33](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3153)]
and then the stores. That's where we're heading with the CALL work.

##### **Geohot** [[00:52:41](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3161)]
When you think about `INS is CALL`, the code should be renderable both in C and in assembly. An assembly backend can match the CALL body for `S_ADD_U32` to the real instruction with a PatternMatcher, while a C backend can render the same UOps into this program.

##### **Qazalin** [[00:53:08](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3188)]
Once I finish that, I'll return to optimizing our GEMMs. We're getting our MLPerf time with a GEMM at 40% MFU. NVIDIA has a GEMM at 70% MFU out of the box. I rented a B200 in the cloud, and it's frustrating that NVIDIA gets that speed while we don't.

##### **Geohot** [[00:53:36](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3216)]
I wonder if we should send this picture to AMD and ask them to pay us to fix that. How many GPUs did you sell? Oh, you sold $10 billion in GPUs and we can come here and we can make them 60% more efficient. Okay, so that's worth $6 billion.

##### **Geohot** [[00:54:01](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3241)]
I'll do it for one.

##### **Qazalin** [[00:54:03](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3243)]
We're already about 5-10% there with FlashAttention.

##### **Geohot** [[00:54:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3250)]
There's also nothing fundamental about that. There's nothing fundamental about AMD's terrible MFU. It's just stupid.

##### **Qazalin** [[00:54:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3266)]
This is hard because nobody can just put an assembly problem into Codex. Even Astra is hilariously bad at assembly.

##### **Qazalin** [[00:54:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3283)]
This needs more fundamental tooling. I can't keep MFMA busy during the gaps because my VGPRs are saturated. AMD hand-wrote the register allocation, so we need a solver for that too. They didn't really think through these allocations.

##### **Qazalin** [[00:55:14](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3314)]
And it's not really something that they can solve with the LLM either.

##### **Geohot** [[00:55:19](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3319)]
AMD doesn't make this easy to code. NVIDIA lets different warps in a specialized kernel use different numbers of registers, and I believe RDNA4 does too. CDNA doesn't, so you have to make the whole thing work with a single warp.

##### **Geohot** [[00:55:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3343)]
So the latency hiding you get is the latency from like, you don't get any warp latency hiding basically. You have to only schedule like one instruction per slot. So this would be kind of annoying to fix, but I'd still fix it. I'll send that picture a little bit.

##### **Geohot** [[00:55:57](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3357)]
I'll also send, you want me to send your bug report? Yeah, I think. Yeah, I'll send, I'll send your, I'll send that, I'll send that gist along too.

##### **Geohot** [[00:56:20](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3380)]
Cool. Raine, do you want to talk about RDNA3?

##### **Raine** [[00:56:28](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3388)]
I've been thinking about how to implement the bodies for x86 instructions as CALLs instead of INS. I've looked at Qazalin's Codegen work, but the main question is how to bind the operands without traversing the entire upstream graph.

##### **Raine** [[00:56:51](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3411)]
Something I've been trying to work on.

##### **Geohot** [[00:56:54](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3414)]
Why would you have to traverse the entire upstream graph?

##### **Raine** [[00:56:58](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3418)]
To know what stop, like at what point you're going to stop to find the operands that you're binding to. Like to find the op that's in the source of the, like of the instruction call.

##### **Geohot** [[00:57:17](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3437)]
I still don't really understand this. I mean, if you look at how it's done for like the, like you think about that, that screenshot that was posted with the AMD stuff. I mean, you should basically, when you render it, have it look like this. Are you saying it's hard to know, like.

##### **Raine** [[00:57:34](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3454)]
Like to construct the exact UOP implementation of a certain instruction.

##### **Chenyu** [[00:57:38](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3458)]
Yeah.

##### **Raine** [[00:57:39](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3459)]
That's what I mean. I want to generate it automatically from the UOp that `.ins` is called on, pruning the graph to bind the operands passed in.

##### **Geohot** [[00:57:54](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3474)]
I see.

##### **Raine** [[00:57:55](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3475)]
That way you wouldn't have to model the operands explicitly. Some vector operations in x86 stack lowering do need explicit modeling, but I hoped for a general solution.

##### **Geohot** [[00:58:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3490)]
I think the right approach is to hand-specify the UOp graph for each instruction. The current instruction selection is ad hoc. In the future, the simplest way to add a processor to tinygrad should be to write UOp implementations for its instructions, then make the instruction selector use those implementations.

##### **Raine** [[00:58:47](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3527)]
Okay. So it goes like both ways.

##### **Geohot** [[00:58:50](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3530)]
It should go the other way. Instead of treating the current instruction selector as the source of truth, write the UOp implementations as the source of truth and derive instruction selection from them.

##### **Raine** [[00:59:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3544)]
Okay.

##### **Geohot** [[00:59:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3544)]
And I think that's going to help.

##### **Raine** [[00:59:06](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3546)]
My PR is mostly x86-specific. I'll rely on Qazalin's Codegen fixes, including custom functions. Once those merge, I hope to upstream and clean up the RDNA3 work too.

##### **Geohot** [[00:59:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3566)]
That would be nice. Sounds good. Next, Comma.

##### **Chrism** [[00:59:36](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3576)]
Yeah. So I think Comma is generally happy. However, they have some complaints about HCQ2.

##### **Chrism** [[00:59:42](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3582)]
So both these issues. The second one, I don't know if the second one is a real issue. But the first one is definitely a real issue, which is that our error handling is not the same as it was previously in the sense that, you know, if someone were to unplug the USB GPU, it would just hang forever.

##### **Chrism** [[01:00:08](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3608)]
I don't know how easy it is to restore the error handling. We need to check the libusb return values. And I don't know how easy it is to add that to HCQ2.

##### **Chrism** [[01:00:24](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3624)]
I think we need some form of error handling.

##### **Geohot** [[01:00:26](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3626)]
Yeah, yeah, yeah. We want error handling in general in HCQ2. Nimlgen, maybe this is the highest-priority HCQ2 fix, even above OpenCL. We definitely need to avoid hanging and handle errors.

##### **Chrism** [[01:00:48](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3648)]
The other one, so the second report, I'm not convinced is a real bug report. I don't know. We can think about what we want to do about this. But basically, they say like, oh, if we have an error in the process, we want to be able to recover the error. And I don't know if that's a reasonable expectation.

##### **Geohot** [[01:01:07](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3667)]
You mean the one where device. The device lock not released after open failed.

##### **Chrism** [[01:01:11](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3671)]
Yeah, but specifically the thing he wants to do is he wants to reopen the like he wants to recover from the error in the same process.

##### **Geohot** [[01:01:20](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3680)]
Oh, no.

##### **Chrism** [[01:01:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3682)]
Yeah.

##### **Geohot** [[01:01:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3682)]
Yeah, that's yeah, that's a one fix. But yeah, we definitely fix the other one. Yeah. Yeah, you couldn't have that error.

##### **Geohot** [[01:01:38](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3698)]
Yeah, I was kind of like, this doesn't make sense. Yeah, easy.

##### **Chrism** [[01:01:42](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3702)]
Certainly not easy for us to test.

##### **Geohot** [[01:01:46](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3706)]
Yeah. Bounties. We still got that. I don't know where we are in that. That GPU ocelot one. Because I guess I'm kind of managing that.

##### **Geohot** [[01:02:04](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3724)]
We also have a RTX 3090 support. The guy still seems active. So that's a bounty. So bounty locked on that.

##### **Geohot** [[01:02:24](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3744)]
And GPU ocelot. Is that just waiting for me to merge or is there something else?

##### **Chrism** [[01:02:30](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3750)]
I think he said he was going to work on something and then didn't work on it. I don't think there's been any updates since then.

##### **Geohot** [[01:02:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3755)]
He says he'll address the review in his next round of commits. Okay, we'll wait a week. So that one's blocked on this.

##### **Qazalin** [[01:02:50](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3770)]
Okay. I think that's everything.

##### **Geohot** [[01:03:00](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3780)]
See my post about Qwen3.8-27B. You can see the red line rising a little. I'm happy about that. We now have by far the fastest Qwen3.8-27B on a 7900 XTX. If you have a 7900 XTX, consider switching to tinygrad. We'll have vision support someday too.

##### **Geohot** [[01:03:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3815)]
If anyone actually uses local LLMs. I think the only LLMs I've found useful are at the GLM-5.2 or GLM-5.3 level. Below that, they aren't quite usable for me.

##### **Wozeparrot** [[01:03:58](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3838)]
I thought DeepSeek V4 Flash was somewhat usable.

##### **Geohot** [[01:04:02](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3842)]
How much did you use it?

##### **Wozeparrot** [[01:04:05](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3845)]
I use it to fix like one thing and it seemed okay. It was really slow though. So I was running it locally.

##### **Geohot** [[01:04:12](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3852)]
We stood it up on one of the Tiny Boxes. It was fast, but I found that it talked itself in circles a lot. Maybe DeepSeek V4 Flash is the size where it starts to work. I tried using it to play Pokemon, but the provider I had didn't work.

##### **Wozeparrot** [[01:04:35](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3875)]
I wanted to try 4.1 flash, but 4.1 flash is like so much bigger than 4 flash and it doesn't fit on my laptop.

##### **Geohot** [[01:04:43](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3883)]
GLM-4-Flash fits on your laptop?

##### **Wozeparrot** [[01:04:44](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3884)]
Yeah, it's about 118 GB.

##### **Geohot** [[01:04:52](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3892)]
Oh, you got 128?

##### **Wozeparrot** [[01:04:55](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3895)]
I have a 128 GB Strix Halo.

##### **Geohot** [[01:05:01](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3901)]
Interesting. And it was slow. Were you using tinygrad? I mean, it should be able to get something like 20 tokens per second.

##### **Wozeparrot** [[01:05:13](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3913)]
Yeah, but even for most like interactive agentic stuff, 20 tokens per second is pretty slow.

##### **Geohot** [[01:05:18](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3918)]
Yeah. All right.

##### **Geohot** [[01:05:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3922)]
All right. We're, we're, we're, I mean like local, this is eventually going to happen. Like local LLMs are eventually going to happen. Maybe we're still like six months to a year away. Also just something to think about for after, for after the AMD contract's done. I think our new thing is going to be replacing the SG Lang servers we have running with tiny grads.

##### **Geohot** [[01:05:48](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3948)]
We're getting some fast Kimi on our-

##### **Chrism** [[01:05:53](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3953)]
Comma keeps complaining about Kimi being offline.

##### **Geohot** [[01:05:56](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3956)]
Well, Comma can pay us. No, we'll put Kimi back. But those machines are busy making money, right?

##### **Wozeparrot** [[01:06:10](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3970)]
Has there been an update on the secret project?

##### **Geohot** [[01:06:14](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3974)]
On the secret project? Yeah, the board is shipping tomorrow.

##### **Geohot** [[01:06:22](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3982)]
Assuming the date hasn't slipped; Rob thought it might. The board ships tomorrow. We have 116 of the GPUs and I'm trying to buy more, but they're slow to reply.

##### **Wozeparrot** [[01:06:36](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3996)]
Yeah.

##### **Geohot** [[01:06:38](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=3998)]
So who knows what that means? Yeah. So that's the latest on that. We should, we should have a board to test. Oh, and then also I think, I think Igor is in San Diego. So, is Igor in San Diego?

##### **Chrism** [[01:06:53](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=4013)]
Yep. Yeah.

##### **Geohot** [[01:06:54](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=4014)]
Let's pull eight GPUs out of an AMD2, put the less valuable ones on a board, and see if they work. That's good. Cool.

##### **Geohot** [[01:07:12](https://www.youtube.com/watch?v=RRRxIw3c7K4&t=4032)]
All right. That's the meeting. Thanks everyone.
