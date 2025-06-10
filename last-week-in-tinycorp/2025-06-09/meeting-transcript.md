# 2025-06-09 Meeting

### Meeting Agenda

**Time:** meeting #74, 9am Monday San Diego time
- company update
- fixed multi (and resnet dataloader), faster ci
- linearizer
- viz
- drivers
- cloud, hash
- onnx
- local
- other bounties (lm_eval, AMD_LLVM)

### Last weeks stream:

[Building a ramp for tinygrad](https://youtu.be/QUry9dHC-bk?si=u1WzkL0G4t81WjoY)

### Audio

[Youtube Link](https://www.youtube.com/watch?v=axTYYYYOHHY)

### Highlights

- **[Company Update](#geohot-000029)**: No boxes shipped last week due to cases delayed in China; supply chain issues persist, tariffs being paid.

- **[Code Refactor and Cleanup](#chenyu-000104)**: Refactoring and cleaning Tinygrad, including ResNet fixes and faster CI; priority is simpler code, better visualization, and improved developer experience.

- **[Improved Developer Experience](#geohot-000133)**: Aim for faster, simpler, reliable, and easy-to-debug environment; distinction between user errors (early catch and clear messages) and internal errors (understandable reporting).

- **[Linearizer Refactor](#chenyu-000254)**: New linearizer is simpler, leading to easier debugging; increased focus on addressing linearizer failures.

- **[Visualization Tools](#geohot-000530)**: Enhanced visualization to include kernel execution timing, memory management, and debugging features like tracking NaNs.

- **[Kernel Debugging Visualization](#qazalin-000753)**: Added click-through visualization from kernel graphs to code generation for easier debugging.

- **[Driver Stability (AM)](#nimlgen-000937)**: Fixed numerical issues (NaNs in BERT/ResNet) due to Linux kernel relocating locked pages; solution is temporary using OS system calls, further cleanups planned.

- **[Driver Development](#nimlgen-001443)**: NVIDIA driver booting on 3090/4090, initial support for 5090 machines available; ongoing work on abstraction and unification.

- **[Cloud System Updates](#wozeparrot-001652)**: Keccak hashing merged; focus on dynamic batch sizing and replacing provisioning stack with cloud file system; addressing stability issues with remote auto mode.

- **[ONNX Parser Improvements](#chenyu-001905)**: Custom ONNX parser passed, simplifying the ONNX operations pipeline significantly; verification that weights load directly to devices.

- **[Local Kernel Masking Bug](#ignaciosica-002217)**: Ongoing work on fixing masking bug affecting code generation in vectorizer and expander; visualization scripts updated and upstreamed.

- **[Benchmarking and LM Evaluation](#wozeparrot-002415)**: Progressing LM evaluation tasks, especially aligning AMD results with SG Lang; adjustments ongoing to match benchmark accuracy.

- **[AMD LLVM Backend](#b1tg-002550)**: Small performance difference (~1-3%) from AMD's HIPCC linked to instruction ordering and register pressure; optimizations and block reordering features added for testing.

- **[General Developer Experience](#chenyu-002904)**: Developer experience prioritized, with feedback actively sought from users, especially largest user Comma; rapid addressing of usability concerns and error handling.

- **[MLPerf and Training Benchmarks](#chenyu-003044)**: Next MLPerf submission deadline October 10; challenges with increasing model complexity and hardware requirements, especially Llama 405B.

- **[Tinygrad Diffusion Use](#chenyu-003940)**: Plans to support Comma’s diffusion models for benchmarking against Torch; aim for improved usability and performance comparison.

- **[Short-term Priorities](#chenyu-004027)**: Developer and user experience highlighted as primary short-term goal, ensuring clear error reporting, debugging, and efficient development workflows.


### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=axTYYYYOHHY&t=0)]
Geohot, Chenyu , Wozeparrot are here in the San Diego tinygrad office

##### **Chenyu** [[00:00:06](https://www.youtube.com/watch?v=axTYYYYOHHY&t=6)]
Okay, everyone here? Kind of?
More or less? Okay.
Okay, let's start with company updates.

##### **Geohot** [[00:00:29](https://www.youtube.com/watch?v=axTYYYYOHHY&t=29)]
I don't know, boxes are shipping, kind of.

##### **Chenyu** [[00:00:33](https://www.youtube.com/watch?v=axTYYYYOHHY&t=33)]
We didn't ship any new box last week.

##### **Geohot & Chenyu** [[00:00:35](https://www.youtube.com/watch?v=axTYYYYOHHY&t=35)]
Geohot:We didn't ship any boxes last week, that's true, because of cases, yeah.
Geohot: They're getting airship from China, I don't know.
Chenyu: Supply chain's hard.
Geohot: Yeah, supply chain's hard.
Geohot: And we're paying tariffs on them, so I hope you all appreciate it.
Chenyu: Great.
Geohot: Yeah, I don't think we have anything to say about the other thing.

##### **Chenyu** [[00:01:04](https://www.youtube.com/watch?v=axTYYYYOHHY&t=64)]
So I think the thing that we discussed in the office was we want to do some refactors, some cleanups, we added a bunch of new features and something in the middle, so many things look messy and we want to clean those up.
And also improve the developer's experience.
So that leads to some fixed ResNet and faster CI.

##### **Geohot** [[00:01:33](https://www.youtube.com/watch?v=axTYYYYOHHY&t=93)]
Yeah, no, when we have to make Tinygrad simpler, we have to go back to line counts, visualization tools, just things that make this project fun to develop for.
What makes things fun?
Things that are fast, things that are easy to understand, things that are reliable, things that are simple.
What makes things bad to develop?
Things that are slow, long repl times, flakiness, having no insight into how things work, things being hard to debug, all that.
The push is going to be for visualization tools, for improved developer experience,

##### **Chenyu** [[00:02:18](https://www.youtube.com/watch?v=axTYYYYOHHY&t=138)]
Better error messages in general or more actionable error message, not just somewhere something said it failed.

##### **Geohot & Chenyu** [[00:02:26](https://www.youtube.com/watch?v=axTYYYYOHHY&t=146)]
Geohot: Well, I mean, we have to separate this concept of like user error from internal error.
Chenyu: Yeah, but most of the errors we are talking here are internal errors.
Geohot: No, look at the ignore out of bounds one, right? Like look at the one that we're hitting now when I try to merge that ignore out of bounds thing.
It's not an internal error, it's a user error.
Chenyu: Ok, yeah, what specifically?
Geohot: Now we could probably catch it earlier.
Now if we are going to find user errors, we want to catch them as soon as possible, try to link it back.
There's tons of ways to make user errors.

##### **Chenyu & Geohot** [[00:02:54](https://www.youtube.com/watch?v=axTYYYYOHHY&t=174)]
Chenyu: Yeah, 
Geohot: Reshape a tensor wrong
Chenyu: Yeah, so I think for user errors, we try to catch it earlier, we try to provide actionable ways for users to resolve stuff.
For internal errors, it should at least be understandable and 
Geohot: Linearizer failure.
Chenyu: Uh, Yes. So that's my plan and focus next. We can move on to the next point.
So with a new linearizer refactor, things are a lot easier. I tried to write it.
I can pretty much understand it. I think the idea is straightforward.
And now we have a lot more linearized failures.
I think as part of it, I will see how I will fix it.
But I think in terms of the idea, the idea is definitely simpler than before.
That's nice.

##### **Geohot** [[00:03:48](https://www.youtube.com/watch?v=axTYYYYOHHY&t=228)]
I'm glad it's understandable because the scheduler is about to look like that too.

##### **Chenyu** [[00:03:52](https://www.youtube.com/watch?v=axTYYYYOHHY&t=232)]
Great.
No, I think definitely the visualization tools helps.
And one way I
I did to understand linearizer is I try to write some very simple kernels, like something like A plus B or like, I don't know, matmul of two metrics and stuff like that.
Gradually apply optimization actions and see how those things got linearized.
I think that's helpful.
Maybe I would, at the end of this, I can have like,
Small tutorial or like kernels that gradually run public complexity.
And by watching how those kernels got built, you can understand how this works better.
That's how I understand it.
But the goal is to try to fix as many linearizer failures as possible.
Now we print them and complain very loud.
You will see that everywhere we apply beams and in CI and such.
And yeah, that's linearizer.
And we can move on to VIZ are very important to us.

##### **Qazalin** [[00:05:05](https://www.youtube.com/watch?v=axTYYYYOHHY&t=305)]
Back in bit, building VIZ for time.
It's really hard to build a scheduler when there is no conception or a way to visualize kernels in a line.
So yeah, we can manage that soon, making progress on a branch.
If George, you want to talk about what we discussed?

##### **Geohot** [[00:05:30](https://www.youtube.com/watch?v=axTYYYYOHHY&t=330)]
Yeah, so yeah, it's it's the current viz stops basically at the kernel level and says almost nothing about a bunch of really important things.
So like we don't know which kernels run when and we don't know how memory is assigned.
So we have stuff like Memory Planner, but Memory Planner is not in the new architecture yet.
Memory Planner operates on these schedule item things, and these schedule item things are not UOPs.
We have almost no insight into them.
We're lucky that that thing doesn't seem to have too many bugs, but I think if we have an understanding of how...
We're basically missing an entire part of how kernels, like, okay, great, you have this graph, and then we run this graph on the GPU.
Okay, how?
Yeah, so just stuff to understand that whole missing middle part, and it'll make some scheduler things a lot easier to debug.
Like that splitting one where the kernels end up being bad.
You almost want to be able to click on a kernel and see the input and output tensors.
I think we could even get to that point.
There's no reason that everything's not reconstructable.
So we could actually see, OK, here at this step, what actually happened.
This is the right tool if you want to figure out if there's NANs in your model.
Well, where did the NANs start?
So yeah, run the thing and maybe things that have NANs light up red or something.
But that's the right interface that you want it on, right?
Because think about in the current viz, I'm not saying that's an actual practical use case, but in the current viz, think about where you'd want to put it if you wanted to show which steps produce NANs.
There's nowhere to really put that, and that's what we want in the new stuff.

##### **Qazalin** [[00:07:53](https://www.youtube.com/watch?v=axTYYYYOHHY&t=473)]
This week I just added the functionality that when you click on the kernel graph, you can go to the code gen rewrite.

##### **Geohot** [[00:08:01](https://www.youtube.com/watch?v=axTYYYYOHHY&t=481)]
Yeah, I saw that at Gitmerge.
I haven't tried it yet, but I'm excited about that.
Yeah, this should all be...
The value prop of Tinygrad is that all of this stuff is in one unified framework.
And it should be really easy to jump between the overworld and the kernel world.

##### **Qazalin** [[00:08:21](https://www.youtube.com/watch?v=axTYYYYOHHY&t=501)]
I was thinking of having something that lights up parts of the memory when kernels write to it.

##### **Geohot** [[00:08:30](https://www.youtube.com/watch?v=axTYYYYOHHY&t=510)]
Yeah, yeah, like you could click on a kernel.
Well, so the other thing about this whole time project is you have to separate the, like, almost the kernel is like a class and the run is like an instantiation.
So you have to separate this concept of the object and the instantiation.

##### **Geohot & Chenyu** [[00:08:51](https://www.youtube.com/watch?v=axTYYYYOHHY&t=531)]
Geohot: Like the type and the instantiation. What are the real words for that?
Chenyu: That sounds correct. Yeah.

##### **Chenyu** [[00:09:00](https://www.youtube.com/watch?v=axTYYYYOHHY&t=540)]
The definition, maybe?

##### **Geohot** [[00:09:03](https://www.youtube.com/watch?v=axTYYYYOHHY&t=543)]
Yeah, yeah, yeah.
And then like, especially with how we do the JIT, I mean, it's really nice how we do the JIT and it's like, it's this capturing JIT, so that like, it's not like your thing is going to be full of all this spam.
Once you've seen one of the JITs, you've seen everything.
It's not like, okay, a few pieces of memory change, but in a very defined way.
So that should make debugging pretty easy.

##### **Chenyu** [[00:09:29](https://www.youtube.com/watch?v=axTYYYYOHHY&t=569)]
Cool.
Okay, let's move on to driver.

##### **Nimlgen** [[00:09:37](https://www.youtube.com/watch?v=axTYYYYOHHY&t=577)]
Yeah, so for AM stability, this week I fixed the 9-ish in BERT and I think all the other numerical problems in AM.

##### **Geohot** [[00:09:47](https://www.youtube.com/watch?v=axTYYYYOHHY&t=587)]
What was it?

##### **Nimlgen** [[00:09:51](https://www.youtube.com/watch?v=axTYYYYOHHY&t=591)]
It was the Linux just relocate pages, which were locked.
And...
The reason we saw NANs is because we use the locked pages to copy to the GPU.
So basically, we copy the wrong data to the GPU after some time.
So it just was randomly.

##### **Chenyu** [[00:10:14](https://www.youtube.com/watch?v=axTYYYYOHHY&t=614)]
No, I think it's yesterday.

##### **Geohot** [[00:10:16](https://www.youtube.com/watch?v=axTYYYYOHHY&t=616)]
So it's which is reallocating pages?
Oh, no, this one.
Yeah.
Yeah.
Wait, it's not a fixed reg update.
Which PR is this?

##### **Wozeparrot** [[00:10:29](https://www.youtube.com/watch?v=axTYYYYOHHY&t=629)]
I don't particularly like the way... I feel like there's too many random OS.system calls.

##### **Geohot** [[00:10:36](https://www.youtube.com/watch?v=axTYYYYOHHY&t=636)]
Where there are OS.system calls.

##### **Wozeparrot & Geohot** [[00:10:39](https://www.youtube.com/watch?v=axTYYYYOHHY&t=639)]
Wozeparrot: The way he fixed this is... The way Nimlgen fixed this is an OS.system call.
Geohot: Oh, this.
Wozeparrot: Yeah. It feels really jank.
Geohot: Disable migration of locked pages.
Interesting. Okay, so how is this supposed to work?
How can you migrate a locked page?

##### **Nimlgen** [[00:11:15](https://www.youtube.com/watch?v=axTYYYYOHHY&t=675)]
No, it's fine.
I mean, like they say, it's fine because they have some algorithms to compact memory.
So to allocate larger chunks so they can relocate them.
With locked, they guarantee that it's not on the disk and you won't get a page fault.
But once your process worked out, they can just optimize memory space.

##### **Geohot** [[00:11:38](https://www.youtube.com/watch?v=axTYYYYOHHY&t=698)]
Whoa, OK.
Well, that's a foot gun.
I always assumed locked pages meant that it was locked and you got that address all the time.
All right, well.
Yeah, no, we should definitely not be using
Oh, but you have to be sudo for that.
I know, it's really jank.
Yeah, yeah.

##### **Wozeparrot** [[00:11:59](https://www.youtube.com/watch?v=axTYYYYOHHY&t=719)]
The other way is to give Python caps as admin, but... Well, yeah, Python has caps as admin, actually.
Does it currently?
I think we currently give it some stuff.
I don't know if we give it caps as admin.

##### **Geohot** [[00:12:10](https://www.youtube.com/watch?v=axTYYYYOHHY&t=730)]
I think we do, yeah.

##### **Wozeparrot** [[00:12:13](https://www.youtube.com/watch?v=axTYYYYOHHY&t=733)]
Oh, okay.
Then you can just write to it directly.

##### **Geohot & Nimlgen** [[00:12:16](https://www.youtube.com/watch?v=axTYYYYOHHY&t=736)]
Geohot: Yeah.
Nimlgen: No, no, no, no. Because kernel checks that you actually user should be like zero.
Nimlgen: UID should be zero. Not only capsys admin.

##### **Geohot** [[00:12:27](https://www.youtube.com/watch?v=axTYYYYOHHY&t=747)]
Wait, the kernel checks UID zero and not capsys admin?
No, it shouldn't.

##### **Nimlgen** [[00:12:33](https://www.youtube.com/watch?v=axTYYYYOHHY&t=753)]
Yeah.
I just try to write it directly.
It can open it for right.

##### **Geohot ,Chenyu & Nimlgen** [[00:12:40](https://www.youtube.com/watch?v=axTYYYYOHHY&t=760)]
Geohot: All right.Yeah, I believe you.
All right.Well, the kernel moves the lock.
Someday we're going to get rid of the kernel.
Chenyu: Great.Great.
Geohot: I can move locked pages. Cool.
Nice work finding that. Yeah.
Two other things to talk about.
We still got to fix the copy out speed of the USB.
Nimlgen: Yeah.
Geohot: I bought a... Oh, this is flaky.
I'll remove that.

##### **Chenyu** [[00:13:14](https://www.youtube.com/watch?v=axTYYYYOHHY&t=794)]
Yeah. Sorry.
Before we move on to a new point, so the NAN issue is fixed.
Does that mean we can run RetinaNet with AM now?

##### **Nimlgen** [[00:13:25](https://www.youtube.com/watch?v=axTYYYYOHHY&t=805)]
Yeah, I haven't tried RetinaNet.
I just .

##### **Chenyu** [[00:13:29](https://www.youtube.com/watch?v=axTYYYYOHHY&t=809)]
He can probably try it later.

##### **Geohot** [[00:13:32](https://www.youtube.com/watch?v=axTYYYYOHHY&t=812)]
Yeah, I can give it a try.
Cool.

##### **Nimlgen** [[00:13:35](https://www.youtube.com/watch?v=axTYYYYOHHY&t=815)]
Yeah, I tried BERT and ResNet, and the issue seems gone.

##### **Chenyu & Geohot** [[00:13:40](https://www.youtube.com/watch?v=axTYYYYOHHY&t=820)]
Chenyu: Yeah, BERT is still out of memory, I think. Great.
Geohot: I love when we actually root cause things, and it has a clear root cause.

##### **Chenyu** [[00:13:49](https://www.youtube.com/watch?v=axTYYYYOHHY&t=829)]
I think for stuff like that it's also probably useful to have at least some comments saying why you put sudo here.

##### **Geohot** [[00:13:57](https://www.youtube.com/watch?v=axTYYYYOHHY&t=837)]
Well, I mean, the sudo is, yeah, you got to write to this thing.
It's clear what the code is doing.

##### **Chenyu** [[00:14:02](https://www.youtube.com/watch?v=axTYYYYOHHY&t=842)]
Yeah, but it's not clear why it's done this way, right?
If Wozeparrot has questions on that.

##### **Geohot** [[00:14:08](https://www.youtube.com/watch?v=axTYYYYOHHY&t=848)]
Yeah, yeah, yeah.
A few more comments there that say basically, locked pages don't behave how you think they do.
But yeah, we definitely got to do something about the copy out speed.
I ordered a...
I woke up at 4.30 in the morning last night and I saw the thing with the new SMU and I'm like, whoa, I can buy 9060s.
And then I saw them on Amazon on my phone and then I was like, all right, I'll get my laptop out and buy one.
So we got a 9060 coming.
It'll be here tomorrow.
But yeah, we got to get this copy out fixed.
What's the latest on that?

##### **Nimlgen** [[00:14:43](https://www.youtube.com/watch?v=axTYYYYOHHY&t=883)]
So no major updates on this.
The copy out speed, yeah.
Yeah.
Yeah.
So we're on BD, actually.
I just ported the whole thing we had to the 3090 and 4090.
So yeah, it should also boot there.

##### **Geohot** [[00:15:04](https://www.youtube.com/watch?v=axTYYYYOHHY&t=904)]
Oh, sweet.
You got the driver booting the 3090 and 4090.
Yeah, I know it's a little different.
This is like intermediate.
You can't boot the GSP directly.

##### **Nimlgen** [[00:15:12](https://www.youtube.com/watch?v=axTYYYYOHHY&t=912)]
Yeah, I mean, it's
So yeah, it's a lot of cleanups to do and actually a lot of things to refactor and unify with AM.

##### **Geohot** [[00:15:34](https://www.youtube.com/watch?v=axTYYYYOHHY&t=934)]
Great, good progress on that.
You got access to the 5090 machines?

##### **Nimlgen** [[00:15:43](https://www.youtube.com/watch?v=axTYYYYOHHY&t=943)]
Yeah, I tried one.
I think H3.
It works.

##### **Geohot** [[00:15:49](https://www.youtube.com/watch?v=axTYYYYOHHY&t=949)]
Yeah, we now have three 5090 machines.
If anyone in here needs a 5090 for something, we can get you on them.
Yeah, we didn't.
I mean, Tinybox V2s are really expensive.
So we'll eventually get some.
But for now, we just have machines with one 5090.
Yeah, they cost us a lot of money.
And the machines with one 5090 are Gen 4.
They're PCI 4.They're not 5.
Again, very expensive.Those CPUs and RAM cost so much.
But yeah, they should be good for any sort of 5090 debugging.
It's nice that we have the NVIDIA driver coming along.
Whenever you write something, when you write something that only targets one thing, your abstractions are never good.
But then, as soon as you go from one to two, your abstractions become good.

##### **Chenyu** [[00:16:44](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1004)]
Yeah.Yeah.
Sweet.OK.
Cloud?

##### **Wozeparrot** [[00:16:52](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1012)]
Merged KACCAK.
Very nice.
I've been working on making the batch size be a variable.
So this way, we're not recompiling the kernel every single time the batch size changes.
We do have a first use case for our cloud, which is just to replace our provisioning stack.
So currently we have two machines that kind of just sit there and do nothing, except they're just a transfer source for the rate array that we preload on the machines as they go out.
So we want to replace that with our cloud file system.

##### **Geohot** [[00:17:38](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1058)]
Yeah, that'll be nice.
We got to make sure we got that 100 gig coming in.
Also, cloud is crashing right now.
Remote is crashing.
I added dash auto, and I mean, I tested it, but I'll take it out.
But I don't understand why that shouldn't work.
Like, that definitely should not crash.
Yeah, no, we should.
It's good to test, because I know there's some other segfault in there, too, and we should figure out what's going on.
I don't know. I don't know.
This one could even be just like a race condition in the startup.
But still, obviously, the remote, it should all be hitting the same back end process.
And I just got to make sure there's no race conditions on the startup.

##### **Chenyu** [[00:19:03](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1143)]
We can move on to ONNX.

##### **Chenyu** [[00:19:05](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1145)]
So ONNX parser, I think it passed.
I will merge that right after the meeting.
So we found one issue and it was fixed promptly.
So thanks for B1TG for that.
Then I think the next step for ONNX is with our own posture, the ONNX op and friends should be a lot simpler.
So that's the next step.

##### **Geohot** [[00:19:37](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1177)]
You mean all the stuff that like, yeah,
It takes them to NumPy.

##### **Chenyu** [[00:19:40](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1180)]
Yeah.
So there are parts that reads stuff.
Now we have a proper parser and parse reading to tensor.
So those are great.
And we also verify that only some things that indicates a number and the subsequent things to parse are done in CPU, but the weights are all done on device.

##### **Chenyu** [[00:20:04](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1204)]
Everything merged this week.
Great.

##### **Chenyu & Geohot** [[00:20:07](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1207)]
Chenyu: Yeah. Testing?
Yeah, so we have the script to test hugging face models, but it's not ready to be put in CI yet.
I give it a try, and I found a bug.
So there are things to improve, but it definitely helped catching other things in the ONNX parser, so we already got values from it.
Geohot: How slow is it?
Chenyu: So the problem is it's fast once you have the model download and you just want to run the model.
That's a few seconds per model.
Geohot: How big are the models?

##### **Chenyu**
Depends on the model.
There are very big ones that we probably want to skip.
Yeah, so we'll give, I don't know, if we can give it a size gate or something and making sure.
It's either we whitelist some models.
So I add one in the CI now to making sure that script runs and the model is good.
It's either a whitelist of some handful of handpicked model, or we have a selection criteria.
Yeah, there are, for some reason, some models has like 10,000 op nodes, even though the model itself is small.
I don't know.

##### **Wozeparrot** [[00:21:21](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1281)]
It just depends on how it's exported.
Yeah.
Sometimes it doesn't export like attention as like the attention.

##### **Geohot** [[00:21:28](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1288)]
I mean, that's kind of the great thing about Tinygrad though, it shouldn't matter.
Like all of these other ONNX runtime, how you export the model determines your runtime, which is insane.

##### **Wozeparrot** [[00:21:37](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1297)]
And then there's like optimizers that look through the graph and fuse everything back in.

##### **Geohot** [[00:21:41](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1301)]
I mean, yeah, but we have that too, but we're just doing it at like the proper layer, not at the special manipulate the ONNX graph.
So it happens to hit the run end, the runtime just right.

##### **Chenyu** [[00:21:54](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1314)]
Yeah.
Other thing is the TrueFlow 16 or DeepPipe in general, there were some hacks in ONNX and we will get those fixed as well.

##### **Chenyu** [[00:22:04](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1324)]
Great.
I think that's the idea for this.

##### **Chenyu** [[00:22:08](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1328)]
That's ONNX.
Move on to Locals.

##### **Ignaciosica** [[00:22:17](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1337)]
Hi. Hello.
Last week, I've been focusing on the masking bug.
So I posted an update on the Tinygrad dev channel.
So yeah, it hasn't been that easy because it spawns across all code gen.

##### **Chenyu** [[00:22:34](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1354)]
So where is the bug located?
Which part of Tinygrad is it?

##### **Ignaciosica & Geohot** [[00:22:39](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1359)]
Ignaciosica: No, it's in code gen.
But specifically, I could work around it by modifying things in the lower or modifying things in the vectorizer and the expander.
So it's a, yeah, it's, I think it's, yeah.
Geohot: Yeah, but I mean, is this still the bug about the buffer numbering?
Ignaciosica: No, no, that's solved like two weeks ago.

##### **Chenyu** [[00:23:12](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1392)]
This is if you apply, I think, PAT2 or something with padding and masking, the codgen is incorrect.

##### **Geohot** [[00:23:18](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1398)]
Got it.
I mean, yeah, but then, OK, and that's why we haven't merged local.

##### **Chenyu** [[00:23:23](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1403)]
OK, cool.

##### **Geohot** [[00:23:23](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1403)]
But I'm glad the buffer numbering is fixed.
I mean, yeah, this seems more, yeah, if you have bugs in the de-vectorizer or something,
If you have a clean repro of them, I'm happy to look.
I think those things are usually pretty quick.

##### **Ignaciosica** [[00:23:39](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1419)]
Yeah, I'm working on that.
Cool.

##### **Geohot** [[00:23:42](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1422)]
But exciting that locals are going to get merged soon.

##### **Ignaciosica** [[00:23:46](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1426)]
Yeah.

##### **Geohot** [[00:23:46](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1426)]
Yeah, we're going to definitely need them if we're going to work on the MI300X.
Yeah.

##### **Ignaciosica** [[00:23:55](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1435)]
Yeah, OK.
I also upstreamed the visualization script for this thread.
So that's it.

##### **Chenyu** [[00:24:06](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1446)]
OK.
Sounds good.
OK, move on to other bounties.
So lm_eval.
I think it's pretty close.

##### **Wozeparrot** [[00:24:15](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1455)]
It's pretty close.
There's still some other stuff that they haven't fixed.
Like they haven't switched.
We want to use MGSM EN rather than the full GSM 8K because that seems to be what SG Lang is using for their test.

##### **Chenyu** [[00:24:29](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1469)]
So the idea is we want to reproduce.
There was a discussion on Twitter about how AMD's implementation through SGLAN is worse.
It might be a bug in SGLAN. I don't know.
But we want to see if we can reproduce the lm_eval number, at least on this small set.
And by our approach, we should see comparable numbers on AMD and NV.
But it's always good to verify that.
And AMD LLVM, thanks for the fix for MI300X.
I verify that fix it.
So now I think the state is it's just overall like 1% to 3% slower.
And I don't know, B1TG, if you have any insight.
You say that it's not LLVM version and something else.

##### **Geohot** [[00:25:22](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1522)]
What even could it be?
What's left?
What's different?
I mean, AMD is just using that LLVM too.
I'm curious about that.

##### **Chenyu** [[00:25:34](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1534)]
I think he mentioned something about loop splitting.
Is that a flag or something?
Okay, he's talking.
Yes.

##### **B1tg** [[00:25:50](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1550)]
When I was testing the speed, I made a
HIP LLVM backend, using HIPCC, compare the HIP to the LLVM IR, and then compare it to the AMD.
And I found that the optimization happened in the first stage.

##### **Geohot & B1tg** [[00:26:20](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1580)]
Geohot: Specifically what optimization?
B1tg: Regarding instructions.
Geohot: Oh, it's an instruction order issue.

##### **B1tg** [[00:26:34](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1594)]
Yes.

##### **Geohot** [[00:26:35](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1595)]
Yeah, if it's a couple percent in an instruction order issue.

##### **B1tg** [[00:26:40](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1600)]
Okay, I mean, we are always... This has something to do...
Look like the register pressure issue.

##### **Chenyu** [[00:26:46](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1606)]
Oh, register pressure?

##### **Geohot** [[00:26:51](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1611)]
Yeah, yeah.
Instruction ordering can affect register pressure.

##### **Chenyu** [[00:26:54](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1614)]
I mean... Oh, so I made a flag to optionally disable the block reordering.
So I think that's a good start point for those.

##### **Geohot** [[00:27:04](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1624)]
Yeah, I mean, eventually, we're going to want that to be some kind of linear programming solver that says, here's an order to minimize.

##### **Chenyu** [[00:27:12](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1632)]
Yeah, and constraint on register some bonds on those, like, register thingy.
We'll get there.

##### **B1tg** [[00:27:20](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1640)]
The program, the HIPCC do the optimization.
For the LLVM IR, the compiler can't do the optimization.
Yeah.

##### **Geohot** [[00:27:37](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1657)]
If we confirm that's what it is, I mean, that's something that should be in Tinygrad anyway.
So I'm fine with just merging it.

##### **Chenyu** [[00:27:49](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1669)]
OK.
I'll give you one last test on everything that we have run.
And if all looks good, I will merge that and bounty's yours.

##### **Geohot** [[00:27:56](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1676)]
Yeah, just make it the default.
I mean, we should also, we need to kind of refactor.
Now we have AMD LLVM, we have CPU and LLVM, we have PTX and not PTX.
We need to kind of, I mean, I see what it should be.
The device should be created with a list of tuples of renderers and compilers.

##### **Chenyu** [[00:28:19](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1699)]
Why does it need to be a tuple?

##### **Geohot** [[00:28:21](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1701)]
Or maybe a dictionary that names them.
I mean, it's nice because like this also solves like right now for like the null backend, there's no renderer and compiler, but that has to be an explicitly handled case with like an optional, where instead if we just have, yeah, if we have like a dictionary, which maps like a name of the compiler to a tuple of a renderer compiler, then we can like say, oh, hey, the null backend has no compilers available.
Otherwise we take normally the first, but yeah, you can specify with a number.
We should also support device equals.
I fixed one of OpenPilot's complaints, I should fix the other one.
Great.
Yeah, I can do that this week.
I'll do that refactor.

##### **Chenyu** [[00:29:04](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1744)]
Yeah, so we want to focus on developer experience, and that includes all the complaints we get from Comma using Tinygrad, because they are so far the largest user for Tinygrad, so we should prioritize their need.
For anyone in this call, if you use Tinygrad as a user and have development issues, that's not obvious.
What you should do, just let us know.
Post somewhere.
And I promise we will take a look.

##### **Geohot** [[00:29:33](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1773)]
Yeah, how are we doing responding to issues?

##### **Chenyu** [[00:29:36](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1776)]
I am responding to those.
So we at least try RHN.
It will at least be put into a known error or an issue or something else.

##### **Geohot** [[00:29:51](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1791)]
Oh, I'll put a bounty up for these Torch, like linalg.svd.

##### **Chenyu** [[00:29:55](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1795)]
No, so the problem is people will just, at least for the Torch, they just call into Torch.

##### **Geohot & Chenyu** [[00:30:00](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1800)]
Geohot: No, no, no, you can't call into Torch.
No, you have to implement a singular value decomposition in Tinygrad.
Is that doable?
Chenyu: Not clear.
Geohot: What's the algorithm?

##### **Chenyu** [[00:30:08](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1808)]
So usually it's a solver, and you have like iterative approximation that calls something multiple times to one of those decompositions.

##### **Wozeparrot** [[00:30:26](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1826)]
I believe in Torch, a lot of these sync with CPU.

##### **Geohot** [[00:30:31](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1831)]
A lot of you CPU?
No, SVD has to be on GPU.

##### **Wozeparrot & Geohot** [[00:30:34](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1834)]
Wozeparrot:SVD might be, but a lot of these do sync with CPU.
Wozeparrot: Ooh. Yeah, a lot of the lin-alg stuff.
Geohot: Pretty brutal.

##### **Chenyu & Geohot** [[00:30:44](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1844)]
Chenyu: Okay, anyway, it's completely as a bounty, and if someone saw it.
Geohot: Yeah, yeah, let's see if ChatGPT says this is possible or not.
Chenyu: Okay, cool.
So I post the new MLPerf deadline for training 5.1.It will be October 10th.
So Flata, just so you know, I lock the bounty for you, we say six hours.
If you can do that before next round, bounty is yours.

##### **Geohot & Chenyu** [[00:31:18](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1878)]
Geohot: Yeah, do we know what is getting, is BERT going to make it?
Chenyu: I think so.
Geohot: Great.

##### **Chenyu** [[00:31:25](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1885)]
I would double confirm.
They have some meetings.
Can we bring ResNet back?
That is very unlikely.

##### **Geohot** [[00:31:33](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1893)]
Oh.Why'd they remove it?
I mean, and they're going to remove, I think they're not going to remove BERT from the next one, 5.1, but they're going to remove it from 6.0.
And it's like, now you're just, all the models are just like, yeah, it's just like, NVIDIA's trying to pull the ladder up behind them.

##### **Chenyu** [[00:31:49](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1909)]
Yeah, I think the issue, they also discussed this.
I didn't participate in all their training group meetings, but I think they also have this problem that companies are interested to see the actual model that people use.
So people are training those big models, and they are making decisions for what's this.
Sure.
Yeah.
Not many people really benefit from knowing how fast they can trim BERTs.

##### **Geohot** [[00:32:19](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1939)]
Yeah, I don't know.
I mean, it's just like, it's accessible in a way that the other ones aren't.
It's not like, it almost always scales.

##### **Chenyu** [[00:32:29](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1949)]
So the good thing is now we have a daily Cron job that changes ResNet and it's been working correctly.
The only reason it's not properly shown on dashboard is because our dashboard shows data in the past two days.
So we will fix that.

##### **Geohot** [[00:32:52](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1972)]
I'll phrase this MLPerf thing better.
It's like what has changed is the dollars barrier to entry to get on MLPerf has gone up.
Like if you're training 405B, you just can't unless you have a very expensive computer.

##### **Chenyu** [[00:33:12](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1992)]
Yeah, I think that's one main reason why they still keep BERTs.

##### **Geohot** [[00:33:16](https://www.youtube.com/watch?v=axTYYYYOHHY&t=1996)]
Yeah.
I'm not complaining about complexity of the models.
I'm just literally complaining about dollars cost of the computer to run these things.
Yeah.
You look at the Llama 405B, and the smallest one on there, I think, is like 512 H100s.

##### **Geohot & Chenyu** [[00:33:33](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2013)]
Geohot: That's like more money than I've ever had in my life.
Chenyu: Yep.

##### **Geohot** [[00:33:45](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2025)]
What is that?
512 H100 is $15 million?
$10 million?

##### **Chenyu** [[00:33:48](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2028)]
Yeah.

##### **Chenyu** [[00:33:55](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2035)]
Okay.
And we probably will do something to the hlb_cifar Bounty.
I don't think none of those are really good.

##### **Geohot** [[00:34:09](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2049)]
No, yeah.
If you're going to submit code with AI and half-assed effort stuff, just don't.
But if someone really dives into that hlb_c part one and is like, oh, I did a really good job, I went in, found out which kernels were slow and made them fast and re-implemented this and it's good and tested it... regressions tests , yeah.

##### **Chenyu** [[00:34:32](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2072)]
So this is ResNet time after your fix?
Oh, nice.
Because you regressed to five hours, now it's three hours again.

##### **Geohot** [[00:34:41](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2081)]
It looks more stable now.
Are we using AM or AMD to run that?

##### **Chenyu** [[00:34:44](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2084)]
Oh, it's AM.

##### **Geohot & Chenyu** [[00:34:45](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2085)]
Geohot: Great. Yeah, we can get BERT on there too?
Chenyu: Sure, if you want to occupy that machine for another five hours.
Geohot: Why is it five?
Chenyu: On red? Five. We just summed it.
It's five. 300 minutes? Oh, yeah.
It's not 100 minutes.
Geohot: Who made these English units?

##### **Chenyu** [[00:35:11](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2111)]
Yeah, 5.5 includes setup.
0.3 kilominutes.
Okay, I don't know.
Also, BERT doesn't run now.

##### **Geohot** [[00:35:23](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2123)]
Well, we should fix that.
I'm absolutely fine with occupying the machine.
If we need more machines, we'll get more machines.
I have a lot of Tinybox Reds.
Is anyone interested in my Tinybox Red?

##### **Chenyu** [[00:35:35](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2135)]
Yeah. I think that's it for this meeting.
Do we want to quickly go through the bounty list?
Yeah.
Uuuvn, you have anything to add for the thing you are working on?

##### **Chenyu, Geohot & Wozeparrot** [[00:35:48](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2148)]
Chenyu: Any progress or bottleneck?
Geohot: The remote part's ready.
Wozeparrot: I'll look at basic multi-host remote again today.
Geohot: Cool.

##### **Geohot**
I wish someone would take the HVAC decode support on the COVID.
Bounties are like that accessible.
Buffers are GC'd on CPU with Viz.
That's fixable.
I remember we got one for that.
It's a hack.
There's a proper way to do that.
But it requires like, you know, 90% thinking and 10% doing.
Oh, the metal device sync issue.
We always get, I'm almost tempted to delete that one because we always get just junk for that that's like not tested.
The problem with the metal device sync one is people just mess with stuff and then they don't hit the bug.
And you didn't fix it, you just changed things and now the bug happens to not trigger.
So that's what many of the PRs I've seen there are.
I saw some comment about the loop splitting requiring some LLVM thing.
It absolutely does not.

##### **Geohot** [[00:37:32](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2252)]
Why does no one ever do the speed bounties?
They're not that hard.
I don't know.
Yeah.
Okay.

##### **Geohot** [[00:37:57](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2277)]
We gotta figure out how to make more accessible bounties for people.
Yeah.

##### **Chenyu** [[00:38:01](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2281)]
For people in this meeting, any questions or suggestions?
Or any bounties you would like to see?

##### **Chenyu & Geohot** [[00:38:12](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2292)]
Chenyu: Yeah, I mean, that's part of the...
Geohot: Yeah, the mask select being slow.
Yeah, look into why mask select is slow.
I don't think it has to be.
I think that it's like maybe one line of fusion away from fixing it.
Chenyu: Or we want to remove the realizing set item.
Geohot: Oh, yeah.
Chenyu: Yeah, who can?
Geohot: I didn't know there was a realizing set item.

##### **Chenyu** [[00:38:35](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2315)]
Maybe now you can just change to kernelize and it will work.

##### **Geohot** [[00:38:38](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2318)]
No, but kernelize isn't better.

##### **Qazalin** [[00:38:40](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2320)]
No, no, that's fundamental.
That's the issue.

##### **Chenyu** [[00:38:43](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2323)]
Yeah, so that's an issue with...
Version or time of this, right?

##### **Qazalin** [[00:38:50](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2330)]
No, it's about views.

##### **Geohot & Chenyu** [[00:38:53](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2333)]
Geohot: Oh, there's a realize in set item, not get item.
Chenyu: Yeah, get item is set item.
Geohot: Oh, set item. Okay, I thought there was a realize in get item.
That would upset me a lot more.
Chenyu: Oh, set item is... It's a sign. That's a sign.
Geohot: Okay. Yeah, I can think about that. Yeah.
Okay, no, okay.It's in set item and I misread that.
I thought it was in get item.It's a lot better now. Great.
Yeah, no, I thought like our tensor select had to be... No, of course not.

##### **Geohot** [[00:39:25](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2365)]
Great.
Yeah.
What?
Oh, okay.

##### **Chenyu** [[00:39:40](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2380)]
Yeah, so...
Comma is also interested in running Tinygrad on their diffusion stuff, and I think they will provide us a script so we can start to benchmark and see how good or bad we are compared to Torch.

##### **Geohot** [[00:39:50](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2390)]
There was a Comma thread about this.
Yes, and Harold said, no, they don't have access to RAID Dell 2.
Yeah, I saw that.

##### **Chenyu** [[00:40:02](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2402)]
Yeah, so...
Short-term focus will be making developer experience better, user experience better.
Everyone using Tinygrad should feel joy and happy to use it and not dreadful and like unknown errors and frustration.
So that's the idea and direction we'd like to go.
Yeah.
And do we get more questions?

##### **Chenyu** [[00:40:27](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2427)]
If no, I think that concludes the meeting.
Okay.
Yeah, if people have suggestions for what you'd like to see we do more or the things that we are not doing enough, just let us know.
With that, that's meeting for this week.
Thank you, everyone.
And see you next week.

##### **Geohot** [[00:40:51](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2451)]
Thanks.

##### **Chenyu** [[00:40:51](https://www.youtube.com/watch?v=axTYYYYOHHY&t=2451)]
Bye.
