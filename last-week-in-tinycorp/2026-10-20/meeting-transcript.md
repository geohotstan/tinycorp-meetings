# 2026-10-20 Meeting

### Meeting Agenda

**Time:** new meeting #42, 10/20 12pm Hong Kong time
- company update
- MLPerf submission
- course, studentgrad
- assembly and CALL
- STACK, tag, uint
- HCQ2 and tag
- CI VMs
- Comma, bounties, RDNA, LLMs


### Audio

[Youtube Link](https://www.youtube.com/watch?v=xaSzMYpHA9s)

### Highlights

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=0)]
Let's start with company updates.

##### **Geohot** [[00:00:03](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3)]
Lots of stuff on the course, mostly that. We're trying to make a deal to buy a lot of cheap used GPUs, but we'll see if this... What? They are used and broken and terrible. Should we pay $5 million for used, broken GPUs? I don't think so.

##### **Chenyu** [[00:00:36](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=36)]
Sales for the new tinybox?

##### **Geohot** [[00:00:38](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=38)]
Tinybox Flashes are really selling. If you buy a tinybox Flash, we might even lose money, because the price of those stupid R9700s is going up.

##### **Chenyu** [[00:00:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=53)]
By a lot.

##### **Chenyu** [[00:00:59](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=59)]
If we can make the box great for running models, then we can buy more.

##### **Geohot** [[00:01:05](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=65)]
Maybe they're a ripoff. If the other GPUs come through, we don't want these ones. The other GPUs are a slightly cheaper version of these.

##### **Chrism** [[00:01:17](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=77)]
Okay, we'll figure something out.

##### **Geohot** [[00:01:20](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=80)]
Box sales are going. If you have feedback for the website, or you could buy a box...

##### **Chenyu** [[00:01:28](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=88)]
I worked pretty hard to make the site look nice.

##### **Geohot** [[00:01:31](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=91)]
Yeah, you worked very hard on that site.

##### **Chenyu** [[00:01:34](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=94)]
If you see any issue, just post it. Cool. MLPerf submission?

##### **Wozeparrot** [[00:01:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=106)]
All the submissions are in. I pushed everything to the MLPerf branches as well. Everyone else's submissions are out too. Unfortunately, we can't talk about them publicly here, but they're in employees.

##### **Nimlgen** [[00:02:05](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=125)]
Can we talk about the GPT-OSS fiasco?

##### **Chenyu** [[00:02:12](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=132)]
My current impression is that some of the speed difference can be explained by better machines and some issues we have. But for GPT-OSS, it seems like we can do a lot better.

##### **Geohot** [[00:02:30](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=150)]
For LLaMA, I think we know the issue. Using SDMA is largely pretty bad. We should be using CUs; that's what all the fast AMD collectives use. We understand that one. But the GPT-OSS implementation is incorrect. This isn't a secret.

##### **Wozeparrot** [[00:02:56](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=176)]
All of NVIDIA's submissions don't follow the reference.

##### **Chenyu** [[00:03:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=184)]
Not following the reference in what sense? Do they converge faster than they should, or is it an implementation issue?

##### **Wozeparrot** [[00:03:14](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=194)]
They converge the same, but their code doesn't match the reference implementation.

##### **Chenyu** [[00:03:20](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=200)]
My impression from the email thread is that they say the reference is doing more work. I saw eight percent in the email. My math was, if that's eight percent for the mismatch to reference, then give it another ten percent for the machine difference...

##### **Wozeparrot** [[00:03:44](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=224)]
No, that's only part of it. The bigger reason our GPT-OSS is slower is that AMD's submission uses FP4 GEMMs.

##### **Chenyu** [[00:03:58](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=238)]
Oh, okay. I didn't know that, if you've confirmed that's the case.

##### **Wozeparrot** [[00:04:02](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=242)]
We shouldn't talk about that, but we use FP8 for the GEMMs.

##### **Chenyu** [[00:04:07](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=247)]
I know we use FP8 on GPT-OSS. Okay. Just making sure we get this in. We should have our results in the final thing; that's how we get our money. For any known discrepancies...

##### **Wozeparrot** [[00:04:26](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=266)]
I have to see on Thursday, because that's the first review meeting, what the handling of GPT-OSS will be.

##### **Chenyu** [[00:04:35](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=275)]
Don't worry too much. Make sure all our submissions and all the good changes are upstream. We qualify, so we need our results included, but I wouldn't worry too much if everyone else did this.

##### **Wozeparrot** [[00:05:03](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=303)]
It seems most of NVIDIA's submissions are wrong, and AMD copied parts of NVIDIA's submission, so parts of theirs differ too. It's a little unclear.

##### **Chenyu** [[00:05:14](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=314)]
My impression of this round is that everything was hastily put together. Anyway, first priority: make sure our submission is valid and shows up in the final results. They said everything should wrap up in November.

##### **Wozeparrot** [[00:05:39](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=339)]
Yes, I think everything releases on the 16th.

##### **Chenyu** [[00:05:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=346)]
The good changes should be upstream. Then we'll be focusing on the 5.3 models, correct?

##### **Wozeparrot** [[00:05:58](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=358)]
I'll be focusing on GLM-5.3. I don't know if we want a router now, or potentially once our models get faster.

##### **Geohot** [[00:06:11](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=371)]
We definitely want a router. It shouldn't just be for tinygrad; it should be for all our SGLang models too.

##### **Wozeparrot** [[00:06:18](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=378)]
Okay, then I'll also work on a router this sprint.

##### **Geohot** [[00:06:22](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=382)]
Great. I want lm.tinygrad.org. Right now I'm using one of my boxes on Tailscale to forward SGLang, Kimi, and GLM. I don't want it to be my one-off infrastructure. I want lm.tinygrad.org to work for everyone in the company, and everyone to be able to use any LLM we're hosting. The first step to being an inference provider is being an inference provider for ourselves.

##### **Chrism** [[00:06:58](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=418)]
Is this a router or a reverse proxy?

##### **Geohot** [[00:07:01](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=421)]
I think we want a router, because we want it to actually check the requests. It shouldn't be complex. It's not just a reverse proxy, because I don't want a bunch of ports. I want something that aggregates every model we're running. If we have Kimi and Kimi-tinygrad, we should be able to select that.

##### **Chrism** [[00:07:27](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=447)]
For sure.

##### **Geohot** [[00:07:33](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=453)]
I also want an employee API key, then a [unclear] API key, and maybe even a public API key if people want to try out Blackwell.

##### **Chenyu** [[00:07:50](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=470)]
Good. Anything else?

##### **Wozeparrot** [[00:07:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=473)]
Nope.

##### **Chenyu** [[00:07:58](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=478)]
Next, course and studentgrad.

##### **Geohot** [[00:08:01](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=481)]
We have TAs. Studentgrad is secret; it's not a public repo. It's the reference compiler. I'm on about week five of the course. There's a ton of subtlety in LOAD. You have LOAD, STORE, AFTER, and RANGE, and the complexity created by those four ops is wild. RANGE was the only one that wasn't exactly clear how to resolve, but I have a clear resolution now.

##### **Geohot** [[00:08:44](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=524)]
The problem is, if inside a RANGE you load from and store to the same buffer, what exactly is that supposed to do? If you want to load from the input buffer, you have to make a copy, but then you're not loading from and storing to the same buffer. Or you can store somewhere else. Trying to do analysis when you're loading and storing inside the loop is dumb.

##### **Qazalin** [[00:09:15](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=555)]
Buffer changed.

##### **Geohot** [[00:09:18](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=558)]
Yeah, 'buffer changed while doing iteration,' like Python's error about a dictionary. That'll be an error. We've also always had the question of what happens if you have two parallel stores to the same buffer, not ordered after each other. Which happens first? The answer is a runtime error. We're resolving these little difficulties. Studentgrad has a ton of tests in UIR format that should pass in tinygrad too. We're resolving a lot of ambiguity in the spec.

##### **Geohot** [[00:10:15](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=615)]
When you think about what device HCQ2 is compiling for, there's an answer: it's compiling for the MEC or SDMA, or whatever your computer is doing. It could compile for CUDA Graph or Metal Graph. You have the kernels, and generating the CUDA Graph object that executes them is what it means to compile.

##### **Nimlgen** [[00:11:03](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=663)]
That part is wrong.

##### **Geohot** [[00:11:07](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=667)]
You should have a renderer for CUDA Graph; we basically do. We can have a renderer for SDMA or MEC too. That's the target device, or renderer target: Clang, LLVM, MEC, SDMA.

##### **Chenyu** [[00:11:34](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=694)]
Good. Excited for the course? Are the TAs enough?

##### **Geohot** [[00:11:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=697)]
I think we'll get more. There are a lot of people on the email thread. I was dreaming about Pittsburgh last night. It'll be fun. You're all invited if anyone wants to guest-lecture. You should come to Pittsburgh and guest-lecture.

##### **Chrism** [[00:11:56](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=716)]
Sure. Where is it?

##### **Geohot** [[00:11:59](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=719)]
We're in the Tepper business school.

##### **Chrism** [[00:12:03](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=723)]
Oh, nice.

##### **Geohot** [[00:12:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=724)]
It's a nice room. We got a nice room that seats 134 people.

##### **Chenyu** [[00:12:14](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=734)]
You're closest. Up to you if you want to. Okay, sounds good. Anything else?

##### **Geohot** [[00:12:22](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=742)]
Nope.

##### **Chenyu** [[00:12:24](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=744)]
Next is assembly and CALL. Do you want to come closer?

##### **Qazalin** [[00:12:30](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=750)]
I think it's good now. We emulate the kernel by putting the whole thing into a C kernel. The old emulator would... [Audio cuts out.]

##### **Geohot** [[00:13:06](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=786)]
What's CPUExecutable?

##### **Qazalin** [[00:13:10](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=790)]
We don't really have the infrastructure for this. I have to recompile the same function. Imagine the assembly emulator... [Audio cuts out.]

##### **Geohot** [[00:13:28](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=808)]
It's a CALL. You don't want to recompile it.

##### **Wozeparrot** [[00:13:39](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=819)]
Qazalin, you are slightly cutting out.

##### **Geohot** [[00:13:43](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=823)]
Move a little closer.

##### **Qazalin** [[00:13:45](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=825)]
This would be good infrastructure to have with HCQ2.

##### **Geohot** [[00:13:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=833)]
CALLs should be compiled separately, so they don't have to recompile.

##### **Geohot** [[00:14:06](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=846)]
We should have a good microphone now. I don't know if we're more audible. There we go, now we have a good microphone.

##### **Nimlgen** [[00:14:19](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=859)]
Is that better?

##### **Wozeparrot** [[00:14:23](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=863)]
Sounds about the same.

##### **Geohot** [[00:14:26](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=866)]
Wait, I might change the... No, that should still be right. Better?

##### **Wozeparrot** [[00:14:34](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=874)]
It does sound the same.

##### **Geohot** [[00:14:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=877)]
Okay, we can't hear you now. Try talking again. Maybe it'll work now.

##### **Geohot** [[00:15:17](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=917)]
Can you hear us?

##### **Wozeparrot** [[00:15:20](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=920)]
Can we hear you? Yeah, hello.

##### **Geohot** [[00:15:24](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=924)]
Is it good quality?

##### **Wozeparrot** [[00:15:28](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=928)]
I think Discord compression is doing a lot to make it sound about the same.

##### **Geohot** [[00:15:34](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=934)]
Hopefully the real microphone is more sensitive, at least. All right, go on. What is CPUExecutable?

##### **Qazalin** [[00:15:44](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=944)]
CPUExecutable is the final binary, the binary that has all the functions.

##### **Geohot** [[00:15:52](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=952)]
There shouldn't be an mmap here. There should be a buffer, a CPU buffer. Why isn't it? I know there was another mmap there before.

##### **Qazalin** [[00:16:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=964)]
It was there before.

##### **Geohot** [[00:16:08](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=968)]
My point is that there's no reason a program shouldn't just be in a buffer.

##### **Qazalin** [[00:16:17](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=977)]
Do we care about making everything executable?

##### **Geohot** [[00:16:24](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=984)]
Is that annoying on Mac? There's weird stuff on Mac about that. You have to use MAP_JIT.

##### **Qazalin** [[00:16:42](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1002)]
Yeah, I know there was some...

##### **Geohot** [[00:16:45](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1005)]
There's an easy solution: buffers don't have to be executable when you write to them. When you execute a buffer, it makes it executable if it isn't already. Where else do you want to keep the program? There's no reason this mmap should be different from the other mmap.

##### **Nimlgen** [[00:17:25](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1045)]
Also, I think this is really bufferize, but we can get to that later.

##### **Qazalin** [[00:17:36](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1056)]
The emulator executes the compiler stuff. [Some speech is inaudible.]

##### **Geohot** [[00:17:49](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1069)]
It seems relatively short.

##### **Qazalin** [[00:17:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1073)]
In codegen's __init__, that's all the extra stuff.

##### **Geohot** [[00:18:02](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1082)]
Does it rip the old emulator out?

##### **Qazalin** [[00:18:03](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1083)]
It can rip the old emulator out.

##### **Geohot** [[00:18:10](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1090)]
That's a big plus.

##### **Qazalin** [[00:18:17](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1097)]
We also need to think about where we cache things. In codegen, I'm caching the CALLs in call_cache, like the schedule cache, because you don't want to rerun codegen for an instruction every time.

##### **Geohot** [[00:18:44](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1124)]
That's probably fine.

##### **Qazalin** [[00:18:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1126)]
It's similar to the schedule cache or method cache.

##### **Geohot** [[00:18:52](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1132)]
We can unify them in the future, but this is fine. I'd merge it in a separate PR.

##### **Qazalin** [[00:19:10](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1150)]
I was thinking, if you set DEBUG, we switch it.

##### **Geohot** [[00:19:16](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1156)]
I was kidding about that. There's no reason adding a debug flag should switch your emulator.

##### **Qazalin** [[00:19:27](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1167)]
You don't want that, right? You can select it explicitly.

##### **Geohot** [[00:19:30](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1170)]
That's fine. I was just kidding. Are you good on this?

##### **Qazalin** [[00:19:48](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1188)]
Yeah.

##### **Chenyu** [[00:19:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1193)]
Okay, next is my stuff. I pushed STACK. Last week we discussed it; there was a change I needed to revert, and I reapplied it with some newly found symbolic improvements. Kernels involving STACK should be more efficient now.

##### **Chenyu** [[00:20:14](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1214)]
We also complained about tag and started this big campaign to remove it. We still have three big places using tag: x86, mostly registers and other weird stuff; rangeify, where we put an empty tuple on local buffers; and HCQ2, which I think is done.

##### **Nimlgen** [[00:20:50](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1250)]
HCQ2 is done.

##### **Chenyu** [[00:20:56](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1256)]
That's pretty much it. I don't know what we want to do with x86, because some of it is optimization, and I don't know whether we care about that in x86.

##### **Geohot** [[00:21:07](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1267)]
We definitely don't care about those features. I'd rather not rip the whole thing out.

##### **Chenyu** [[00:21:11](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1271)]
Is there a limit? I can remove a lot, but the generated bytecode doubles in size.

##### **Geohot** [[00:21:18](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1278)]
That's probably fine, depending on what specifically.

##### **Chenyu** [[00:21:23](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1283)]
Some of it is improvements and merging in instruction selection.

##### **Geohot** [[00:21:33](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1293)]
Correctness is fine. Rip any of that out.

##### **Chenyu** [[00:21:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1297)]
Okay, I can take tag. The annoying one is a loop-compare or BACKEDGE thing that already violates SPEC=2 if you run it. I'll look at it. I'll remove the optimizations and keep correctness.

##### **Geohot** [[00:22:01](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1321)]
Then is that the end of tag?

##### **Chenyu** [[00:22:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1324)]
We've already removed a lot. There's no tag in [unclear subsystem] now. There are probably another fifty lines dealing with tagging that we can remove.

##### **Geohot** [[00:22:14](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1334)]
Great.

##### **Chenyu** [[00:22:17](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1337)]
I didn't list this, but with the studentgrad STORE, RANGE, and LOAD discussion, I'm trying to find similar cases in ASSIGN and fix or raise errors accordingly.

##### **Geohot** [[00:22:35](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1355)]
We shouldn't be thinking about those cases at the ASSIGN level. We should be thinking about them at the UIR level.

##### **Chenyu** [[00:22:41](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1361)]
Yes, this is about following the spec we agree on in studentgrad, with ASSIGN following that.

##### **Chenyu** [[00:22:55](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1375)]
An interesting thing: while cleaning up ASSIGN/STORE, one big violator was the counter in Threefry. My draft uses a uint64 counter directly instead of splitting it into uint32s. Doing that made me realize Threefry depends on unsigned integers wrapping. Currently we just assume a uint number is a number, which makes removing the Threefry-specific rules difficult. It's a correctness issue.

##### **Chenyu** [[00:23:42](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1422)]
In the symbolic rules, we can't simply assume a uint number behaves like an unbounded integer. If you have a uint constant of minus one less than three, it shouldn't fold to true, because minus one wraps.

##### **Geohot** [[00:24:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1444)]
How do we have uint constants in the first place? Aren't constants weakint now?

##### **Chenyu** [[00:24:07](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1447)]
Later in codegen, there are places using AND to get the 32 bits.

##### **Geohot** [[00:24:17](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1457)]
So AND is lowered to uint from weakint?

##### **Chenyu** [[00:24:21](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1461)]
Ultimately there are places where you specify uint and use it.

##### **Geohot** [[00:24:27](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1467)]
When you cast minus one to uint, that should wrap. We should make sure constant folding handles wrapping correctly. Studentgrad is careful about all this.

##### **Chenyu** [[00:24:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1477)]
My other draft does that, and I found another uint bug along the way. I'm trying to get to the bottom of it. We have three symbolic rules added specifically for Threefry, making sure it becomes uint32. Those should go away. Whenever we need decomposition, dtype decomposition should generate something similar, basically the same thing.

##### **Chenyu** [[00:25:18](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1518)]
All uints should wrap. For a uint buffer or constant, the symbolic rules cannot assume it won't wrap. I've updated the min/max bounds for those too.

##### **Geohot** [[00:25:29](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1529)]
We may want to consider making buffers not have a dtype anymore.

##### **Chenyu** [[00:25:44](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1544)]
Store everything as uint8, then bitcast when you load?

##### **Geohot** [[00:25:49](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1549)]
Yes. The problem I've always had with Threefry, removing those uint64 things and trying to use dtype decomposition, is that they create a uint64 buffer. I don't know if our decomposition handles that.

##### **Chenyu** [[00:26:05](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1565)]
We have a better way to bitcast now. That's how I removed tag from dtype decomposition, using STACK. We can move in that direction, though there may be alignment issues.

##### **Geohot** [[00:26:26](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1586)]
Maybe I'll post some studentgrad tests. We should add a framework to test them.

##### **Chenyu** [[00:26:33](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1593)]
I have tests to add from this.

##### **Geohot** [[00:26:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1597)]
We can pull some in. I don't want to reveal the tests that are going to be secret for the class.

##### **Chenyu** [[00:26:48](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1608)]
That's only if OpenAI or Anthropic don't use my chat logs to train on them.

##### **Geohot** [[00:26:54](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1614)]
Yeah, that's how they stole the... Okay.

##### **Chenyu** [[00:26:57](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1617)]
I'm excited about this uint work and removing the weird Threefry rules. It'll be very clean at the end. That's pretty much it. We can move on to HCQ2.

##### **Nimlgen** [[00:27:15](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1635)]
HCQ2 is one hundred percent now.

##### **Geohot** [[00:27:34](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1654)]
We got to all of them. Why is WebGPU bad?

##### **Chenyu** [[00:27:41](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1661)]
It's equally bad in CL. The dtype design is bad. [Unclear phrase about the design.]

##### **Geohot** [[00:27:49](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1669)]
You mean WebGPU in general, nothing specific to HCQ2. An interesting thought: instead of WebGPU calling Dawn API bindings, can HCQ2 just output JavaScript?

##### **Nimlgen** [[00:28:11](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1691)]
We were discussing that.

##### **Geohot** [[00:28:13](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1693)]
Something like Node or something. Where does JavaScript run? I don't know how JavaScript works. Is there a JavaScript runtime that supports WebGPU we could use?

##### **Nimlgen** [[00:28:33](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1713)]
It's possible with HCQ2. I don't know if there's a runtime we can test with. The only problem...

##### **Qazalin** [[00:28:42](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1722)]
Chrome.

##### **Nimlgen** [[00:28:44](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1724)]
In that case, we'd have a JavaScript renderer.

##### **Geohot** [[00:28:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1726)]
I think so. We'd have it the same way we have the MEC renderer. The Dawn runtime is completely useless. Nobody's going to use that runtime; people use WebGPU to compile to JavaScript. Can we compile to JavaScript and get a runtime? We need JavaScript with WebGPU.

##### **Nimlgen** [[00:29:19](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1759)]
It's basically like the C-style renderer.

##### **Geohot** [[00:29:26](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1766)]
Why can't we just output JavaScript? Let's write a JavaScript renderer. It's close to C-style, right? We can extend CStyleRenderer to support JavaScript, then extend that for HCQ2 WebGPU, in the same way we output C code.

##### **Nimlgen** [[00:29:52](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1792)]
Yeah.

##### **Qazalin** [[00:30:00](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1800)]
Chrome. Basically all the exporters we have are just HCQ.

##### **Geohot** [[00:30:12](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1812)]
All the what?

##### **Qazalin** [[00:30:16](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1816)]
The exporters.

##### **Geohot** [[00:30:21](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1821)]
Have we cleaned them up?

##### **Qazalin** [[00:30:22](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1822)]
Yes, we have.

##### **Geohot** [[00:30:33](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1833)]
Another HCQ2-adjacent project: I want to make it easy to save JITs on disk, not with pickle. I want to save JITs in safetensors, with UIR in the metadata.

##### **Nimlgen** [[00:30:58](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1858)]
That should be fine. A JIT is already basically one UOp. You can pass it to another device and it'll be fine. The only problem is some metadata for users that we save.

##### **Geohot** [[00:31:23](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1883)]
That's still handled with shapes and stuff. I don't know what your solution is; probably to be less clever and not do that. This is a bigger problem. We should force all the CALLs to reshape to (n,) before passing anything, because that's all that's allowed in PROGRAM. There's no shape allowed in PROGRAM. If we force things to be contiguous before a JIT, I'm fine with that. We should make that change.

##### **Chrism** [[00:32:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1924)]
Maybe the JIT function takes keyword arguments.

##### **Nimlgen** [[00:32:09](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1929)]
Keyword arguments are annoying.

##### **Geohot** [[00:32:15](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1935)]
We should support that with names in PARAM. We have a slot in PARAM and a name in PARAM; we should have keyword arguments. Then that UIR actually is the JIT.

##### **Geohot** [[00:32:36](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1956)]
UIR should be able to reference disk tensors. I'm thinking about LLMs: they have to compile ten prefill/decode helpers. I'd like to compile them all with JIT, create one UIR file, and that becomes the cache for the LLM. It loads fast.

##### **Nimlgen** [[00:33:09](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1989)]
It's not far from that already.

##### **Geohot** [[00:33:12](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=1992)]
It'd be nice to have a disk tensor for it. Right now we load a pickle file. We could load the pickle as a disk tensor. We could do it with a safetensors file that references itself. Instead of slot mappings and names for objects, what if you just reference the disk tensor itself?

##### **Qazalin** [[00:33:51](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2031)]
That's basically what the ONNX exporter does, compile_onnx.

##### **Geohot** [[00:34:01](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2041)]
It uses the disk tensor. Especially with LLMs, I don't want to copy the weights. The thing could include all the loading. It'll be really nice: a 20K UIR file that includes everything.

##### **Nimlgen** [[00:34:25](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2065)]
Including all the HCQ submits.

##### **Geohot** [[00:34:30](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2070)]
It should load basically instantly. One pass finds all the disk copies, batches them, and fires them off. It shouldn't require a compiler.

##### **Nimlgen** [[00:34:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2086)]
The programs won't recompile.

##### **Geohot** [[00:34:48](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2088)]
It shouldn't require a compiler, no.

##### **Chenyu** [[00:34:54](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2094)]
Let's put this in the thread: multithreaded CPU and this.

##### **Geohot** [[00:35:11](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2111)]
Let's get the speedup merged. For multithreaded CPU, are we going to do HCQ2? Have a basic CPU running? We had multithreaded CPU; do you understand why I ripped it out?

##### **Nimlgen** [[00:35:31](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2131)]
Yeah, we need to do it on CALL.

##### **Geohot** [[00:35:35](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2135)]
It's a UOp. On CALL, anyway. Got it.

##### **Nimlgen** [[00:35:45](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2145)]
I'll bring back the worker. The only thing for CPU is to switch everything to take UOp arguments, the same as the other devices. Potentially the worker could be rendered.

##### **Geohot** [[00:36:15](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2175)]
It's our generic queue format. Sounds good. Anything else?

##### **Chenyu** [[00:36:22](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2182)]
Tag is still on the list. You could also remove the rangeify one.

##### **Geohot** [[00:36:28](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2188)]
Rangeify uses it for the local-buffer renumbering thing.

##### **Chenyu** [[00:36:44](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2204)]
I can look. I have a diff I don't quite understand, because I don't quite understand the old rangeify either.

##### **Geohot** [[00:36:54](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2214)]
Nobody understands the old rangeify, and it wasn't even written with AI.

##### **Chenyu** [[00:37:00](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2220)]
But I understand studentgrad's rangeify. I'll take that. I'm excited to have a spec.

##### **Chenyu** [[00:37:15](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2235)]
Next we have CI, and VMs in CI.

##### **Chrism** [[00:37:20](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2240)]
Master broke because it broke the six-GPU NV job.

##### **Geohot** [[00:37:35](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2255)]
Why are we skipping the NV multi-GPU benchmark?

##### **Chrism** [[00:37:40](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2260)]
G1 is offline. I tried rebooting it, and it didn't come back.

##### **Chenyu** [[00:37:44](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2264)]
This is probably a network issue. Can we rerun it? I just want CI to...

##### **Geohot** [[00:37:48](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2268)]
Why aren't these logs expanding? I've seen this.

##### **Chrism** [[00:37:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2273)]
I think that's the issue.

##### **Geohot** [[00:37:55](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2275)]
You think it's GitHub?

##### **Chrism** [[00:37:57](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2277)]
I'll look into it. I think it happens when I deploy to infra. I'm pretty sure GARM restarts, shuts down a socket, and the job doesn't finish reporting.

##### **Geohot** [[00:38:09](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2289)]
I've seen a deploy do something weird before. Got it.

##### **Geohot** [[00:38:23](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2303)]
Do we have GPUs in VMs?

##### **Chrism** [[00:38:25](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2305)]
Yes, all those jobs are running in VMs. The only exception is LLVM Speed.

##### **Geohot** [[00:38:32](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2312)]
What about multi-GPU?

##### **Chrism** [[00:38:34](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2314)]
That was running in VMs too, but G1 is offline after the reboot. The queues got insanely long, so I'm skipping it for now. I'll figure out what's going on.

##### **Geohot** [[00:38:49](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2329)]
Got it. But AMD GPU is running?

##### **Chrism** [[00:38:52](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2332)]
Yes, this one is running.

##### **Chenyu** [[00:38:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2333)]
We also discussed changing all the six-GPU jobs to four GPUs. Four aligns with the other jobs using one GPU, for better utilization.

##### **Chrism** [[00:39:07](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2347)]
That should help NV too, but the bigger issue is that runner being offline. It has a different BIOS version from the other green machines. I talked to Elliot. He thinks tomorrow he needs to unplug it and disconnect the CMOS battery to get back into the BIOS, because we can't get into it right now.

##### **Chrism** [[00:39:38](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2378)]
The only tinybox job not in a VM is LLVM Speed. Obviously, Macs and Comma devices are still on real hardware.

##### **Geohot** [[00:39:52](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2392)]
Why is LLVM Speed not in a VM?

##### **Chrism** [[00:39:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2393)]
I just haven't done it yet.

##### **Geohot** [[00:39:57](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2397)]
Who's looked at that? Nobody. What a waste.

##### **Chrism** [[00:40:00](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2400)]
I saw a screenshot of it the other day.

##### **Geohot** [[00:40:02](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2402)]
I saw a screenshot of it all green at the bottom.

##### **Chrism** [[00:40:08](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2408)]
You can just delete it; that's fine. That means we don't use the H machines.

##### **Nimlgen** [[00:40:13](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2413)]
Wait, what?

##### **Geohot** [[00:40:17](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2417)]
We should test that, though. I want to test PCI.

##### **Chrism** [[00:40:22](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2422)]
The PCI tests run on the current machines. We could use the H machines for something, but we don't. They only have two GPUs. It'd be cool to have tests running on the MI350s, maybe.

##### **Geohot** [[00:40:47](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2447)]
The problem is that we only have two. It's not slow. Do you mean it's slow to start up?

##### **Qazalin** [[00:40:55](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2455)]
Yes, slow to start up.

##### **Nimlgen** [[00:40:58](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2458)]
That's fixable. There's a fix someone can merge.

##### **Geohot** [[00:41:03](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2463)]
The bigger problem is that we're no longer testing a 5090. We're testing 3080s, 4090s, RDNA4, and RDNA3, but no 5090s.

##### **Chrism** [[00:41:28](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2488)]
I can add whatever tests on there. It's a little annoying they only have one 5090 and one MI350.

##### **Geohot** [[00:41:32](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2492)]
I don't love that they're separate machines. The other problem is that 5090s are rare and expensive.

##### **Chrism** [[00:41:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2506)]
I think we're testing 5060s with the Mac.

##### **Geohot** [[00:41:51](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2511)]
Maybe we should swap the 3080s for 5070 Tis.

##### **Nimlgen** [[00:42:02](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2522)]
That works.

##### **Geohot** [[00:42:05](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2525)]
Then we're testing 50s and 40s. I don't care about 30s.

##### **Chrism** [[00:42:10](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2530)]
The 30s have a different boot process.

##### **Geohot** [[00:42:14](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2534)]
The 30s and 40s have the same boot process. The 50s are different.

##### **Chenyu** [[00:42:21](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2541)]
I didn't realize the VMs wipe all caches.

##### **Chrism** [[00:42:26](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2546)]
That's true.

##### **Chenyu** [[00:42:28](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2548)]
But it's surprisingly fast.

##### **Geohot** [[00:42:29](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2549)]
That's an advantage.

##### **Chrism** [[00:42:30](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2550)]
I did need to bump the LLM timeout.

##### **Chenyu** [[00:42:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2557)]
We always want to run it with no cache.

##### **Chrism** [[00:42:43](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2563)]
I also realized we can delete reset process replay. It isn't doing anything.

##### **Geohot** [[00:42:59](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2579)]
The Macs?

##### **Chrism** [[00:43:01](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2581)]
The Macs aren't in VMs. Performance is worse. I haven't benchmarked it significantly, but I fear it may be noisy with two VMs running simultaneously; Metal performance may vary.

##### **Geohot** [[00:43:19](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2599)]
They share a GPU.

##### **Chrism** [[00:43:20](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2600)]
Yes.

##### **Geohot** [[00:43:23](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2603)]
What if we have just one VM on the Mac? We didn't do the kernel workaround, did we?

##### **Chrism** [[00:43:29](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2609)]
We have done that.

##### **Geohot** [[00:43:32](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2612)]
One VM is still nicer if there's no performance hit.

##### **Chrism** [[00:43:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2617)]
I believe there is a performance hit. Seventy percent, maybe.

##### **Geohot** [[00:43:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2626)]
Even one VM at a time is preferable, because we don't want to keep reset process replay around.

##### **Chrism** [[00:43:54](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2634)]
Right, and it clears the cache. I can look into VMs for Comma devices, but I'm worried they're running Linux 4.9.

##### **Geohot** [[00:44:11](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2651)]
If we don't use VMs, can we at least use Docker? I'd be fine with the Commas in Docker.

##### **Chrism** [[00:44:22](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2662)]
I'll look. If we only run one VM on the Mac, maybe there's a better GPU passthrough option, but it's down to what Apple gives you access to.

##### **Geohot** [[00:44:35](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2675)]
I'd like to isolate the Commas more from the network. I want to treat all this infrastructure as basically public.

##### **Chrism** [[00:44:47](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2687)]
Someone could reserve a Comma and say, 'I want to run something on this.' That makes sense. I wonder how fast it is to flash a Comma.

##### **Geohot** [[00:45:00](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2700)]
You'd wear the shit out of the flash.

##### **Nimlgen** [[00:45:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2704)]
It's also pretty slow.

##### **Chrism** [[00:45:12](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2712)]
Maybe we could have an overlay filesystem that doesn't let anything persist across reboots. Reboot the device and get a fresh base.

##### **Geohot** [[00:45:28](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2728)]
I like an untrusted, isolated network where you can connect in, but they can't connect out.

##### **Chrism** [[00:45:36](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2736)]
Right now they all have access to the gateway machines, gateway1 and gateway2.

##### **Geohot** [[00:45:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2746)]
They should have some access, but it should be firewalled.

##### **Chrism** [[00:45:50](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2750)]
I should restrict it to specific ports. Right now they get the whole machine.

##### **Geohot** [[00:45:55](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2755)]
You're saying all the VMs do?

##### **Chrism** [[00:45:57](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2757)]
All the VMs get all the ports.

##### **Geohot** [[00:45:59](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2759)]
We should limit that. All these things should be isolated.

##### **Chrism** [[00:46:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2764)]
That's really stupid. Someone could in theory persist something.

##### **Chrism** [[00:46:13](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2773)]
I'll look into it. Anything else? We need 10-gig network cards. I ordered five for the CI runners, but if we want the other red AMD boxes to be VM hosts...

##### **Geohot** [[00:46:40](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2800)]
They have OCP slots. We can buy three more; I just bought OCP cards.

##### **Chrism** [[00:46:47](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2807)]
I bought five: two for the green machines and three for the red machines.

##### **Nimlgen** [[00:46:52](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2812)]
Those should be fine.

##### **Geohot** [[00:46:57](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2817)]
Great. Maybe we retire the H machines. Let's buy 5070s. They should have the power for them. Slim OC, do we like that? Does it seem quiet?

##### **Chrism** [[00:47:21](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2841)]
Probably.

##### **Chenyu** [[00:47:25](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2845)]
Let's continue with the meeting.

##### **Chrism** [[00:47:28](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2848)]
That's all.

##### **Chenyu** [[00:47:32](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2852)]
Comma happy?

##### **Chrism** [[00:47:35](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2855)]
I haven't heard complaints.

##### **Chenyu** [[00:47:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2857)]
Are they still on a fork?

##### **Chrism** [[00:47:38](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2858)]
No.

##### **Geohot** [[00:47:39](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2859)]
Great.

##### **Chenyu** [[00:47:43](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2863)]
Bounties and RDNA. What's Raine doing?

##### **Geohot** [[00:47:46](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2866)]
I think we're about done. No progress on RDNA. We'll pay out the bounty for...

##### **Chenyu** [[00:47:56](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2876)]
The order one?

##### **Geohot** [[00:47:57](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2877)]
The order one, yes.

##### **Chenyu** [[00:47:58](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2878)]
And you each took one: the Qualcomm emulator and Ocelot?

##### **Chrism** [[00:48:01](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2881)]
I need to do Ocelot.

##### **Geohot** [[00:48:07](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2887)]
The problem is these bounties aren't worth it when they create work for us.

##### **Chrism** [[00:48:13](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2893)]
The Ocelot one is worth it, because we get to delete code.

##### **Geohot** [[00:48:16](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2896)]
We want it. If an LLM says it's fine, it's probably fine.

##### **Chrism** [[00:48:26](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2906)]
I wanted to set up the VMs I can SSH into and keep, so I can spin up a 3080 VM with SM86 and tell an agent to fuzz Ocelot against the real hardware.

##### **Chenyu** [[00:48:37](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2917)]
The problem is they'll find tons of errors. Last time I checked our emulator, I found a bunch of bugs I don't know if I want to fix. I have a list of other bugs.

##### **Geohot** [[00:48:54](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2934)]
You mean the RDNA3 emulator bugs?

##### **Qazalin** [[00:48:57](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2937)]
I fixed a bunch.

##### **Chenyu** [[00:49:01](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2941)]
If you have AI do it, you'll find the most bizarre, weird cases.

##### **Geohot** [[00:49:07](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2947)]
Is that what we want to address?

##### **Qazalin** [[00:49:10](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2950)]
There's a question there.

##### **Chenyu** [[00:49:14](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2954)]
It mismatches the actual hardware.

##### **Geohot** [[00:49:16](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2956)]
It finds mismatches with hardware that has FP8 FNUZ/NaN quirks.

##### **Qazalin** [[00:49:21](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2961)]
The real NaNs, yeah.

##### **Chenyu** [[00:49:24](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2964)]
Our emulator used to have some hacky redirection logic too. I don't know if that's still the case.

##### **Chrism** [[00:49:34](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2974)]
I worry especially about Ocelot, because we're not generating it from anything. It's just more hand-written lines.

##### **Geohot** [[00:49:47](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=2987)]
We'll put 5070s in those machines, then have some big 3080 machines. We can take the H machines offline, or put both MI350s in one.

##### **Chrism** [[00:50:01](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3001)]
I don't know which H machines they're on, or if we can do that.

##### **Chenyu** [[00:50:08](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3008)]
LLMs. B1tg, do you want to add anything? You can also type.

##### **Geohot** [[00:50:18](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3018)]
Good work on the Flash model. I built on top of it and have the branch working. I saw your MTP work too; it's probably better than the Opus one I have. PR 18863 is the big GLM Flash PR.

##### **Geohot** [[00:50:43](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3043)]
By the end of the year, I want to be fully moved to tinygrad for our personal LLM inference. A cool perk of working here is unlimited tokens off any tinybox. Whatever you want tokens for, we've got tokens.

##### **Geohot** [[00:51:04](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3064)]
I tried to run DeepSeek-V4.1-Flash this morning on TA2. It's only supported on MI350, so if we want it, we've got to get it supported.

##### **Chenyu** [[00:51:18](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3078)]
GLM-5.3 and what?

##### **Geohot** [[00:51:25](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3085)]
GLM-5.3 is already running on TA1. On TA2 I tried the new DeepSeek, but the kernels aren't there.

##### **Nimlgen** [[00:51:36](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3096)]
We can...

##### **Geohot** [[00:51:39](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3099)]
Will DeepSeek fit on my fourteen-GPU monstrosity? We're getting a fourteen-GPU machine.

##### **Chenyu** [[00:51:50](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3110)]
The big disk one?

##### **Geohot** [[00:51:53](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3113)]
The disk one's different. That one's apparently built already; I hope those adapters come. We're working on a machine that can run Kimi for around $15,000 at thirty tokens per second.

##### **Chenyu** [[00:52:16](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3136)]
There are a lot of interesting configurations, hopefully showing...

##### **Geohot** [[00:52:21](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3141)]
Why frameworks like tinygrad can work. We'll have our disk driver, our NVMe driver. Are you excited?

##### **Chenyu** [[00:52:38](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3158)]
We'll focus more on making sure tinygrad supports different models on different machines. That stresses our scheduling, dispatching, and launch speed.

##### **Geohot** [[00:52:58](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3178)]
This has immense value. SGLang doesn't work to run DeepSeek 4.1 on MI300. When you run GLM Flash, you get twenty tokens per second. There's a lot of value in supporting diverse LLMs on diverse hardware.

##### **Chenyu** [[00:53:32](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3212)]
I don't know about SGLang, but I've noticed SemiAnalysis shilling for AMD's token speed all the time.

##### **Geohot** [[00:53:41](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3221)]
I saw something about Morgan Stanley downgrading AMD because everyone wants the new NVIDIA GPU. Unless I'm missing something, the new AMD GPU looks strictly better. The MI350X looks amazing.

##### **Qazalin** [[00:54:00](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3240)]
MI450X.

##### **Geohot** [[00:54:03](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3243)]
It looks better than the NVIDIA one. I don't get why everyone's hyped about NVIDIA. The MI355 looks better too.

##### **Qazalin** [[00:54:20](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3260)]
It's faster.

##### **Geohot** [[00:54:23](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3263)]
Certainly faster than the B200, maybe not the B300.

##### **Chrism** [[00:54:29](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3269)]
[Unclear brief remark about AMD.]

##### **Geohot** [[00:54:34](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3274)]
We're big AMD shills now, but only if they come through with this deal. Otherwise we'll have to ramp up the negative PR again. I'm kidding. The negative PR is all devoted to Intel now.

##### **Chenyu** [[00:54:49](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3289)]
Cool. I think that's pretty much it. Anything else for the meeting?

##### **Geohot** [[00:54:54](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3294)]
No.

##### **Chenyu** [[00:54:55](https://www.youtube.com/watch?v=xaSzMYpHA9s&t=3295)]
That's it for this one. Thank you, everyone. See you next week. Bye-bye.
