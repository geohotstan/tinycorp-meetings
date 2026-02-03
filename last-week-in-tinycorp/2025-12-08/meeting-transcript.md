# 2025-12-08 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update
- training loop, LLaMA 8B
- flash attention
- VIZ/Profiling
- drivers
- MESA backend
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=sc6cckdAXy8)

### Highlights

- **[Company Update & Revenue](#geohot-000005)**: Shopify hardware revenue grew from $1.5M to $1.83M (~22%), plus $400k from AMD, putting total revenue up nearly 50% year-over-year; Shopify is used to track and fulfill essentially all box sales.

- **[Hardware Product Status (TinyBox / RTX 6000 / Red V2 / Blackwell)](#geohot-000235)**: RTX 6000 boxes and Red V2 boxes are selling, with first Red V2 units shipped; Blackwell box layout was adjusted (3 cards stacked + 1 offset) and power capped so all GPUs now stay under 80°C and the system is “super stable.”

- **[New Hire Onboarding](#geohot-000263)**: Chris’s first day is acknowledged; Geohot notes he should already know what he’s working on and points him to Julie for any onboarding logistics.

- **[Training Loop & LLaMA 8B Goals](#chenyu-000294)**: Training loop has been updated with debug tooling (schedule hashing, JIT vs non-JIT comparison) and gradient-accumulation plans; they discuss potential “one big gradient” optimizations and sharding complexities, with a target of running LLaMA-8B on an MI350X machine (8 GPUs) in about two hours, mirroring MLPerf results.

- **[FlashAttention Integration & BERT Bring-up](#wozeparrot-000614)**: FlashAttention has been merged into `tensor.py` with prereqs for the backward pass; backward support is expected to land before Thursday so they can run BERT benchmarks on MI350 and MI300 machines, with an explicit goal of having a successful forward+backward BERT run replicated across all big boxes.

- **[Profiling UI & GEMM Optimization](#qazalin-000866)**: Performance monitoring counters (PMCs) are now visible in the profiling studio UI; next step is a memory-access visualizer to show per-thread buffer accesses and coalescing, which will then drive work on making GEMM fast on MI350 (closing the loop between tooling and GEMM performance).

- **[MI350 Bugs, Drivers, & Power Usage](#nimlgen-001068)**: A sporadic MI350 crash involving strange instruction-cache addresses has been partially understood but not reliably reproduced; they suspect context-save/restore features similar to RDNA3 issues. Work continues on the AMD (“AM”) driver for MI350, with hopes it can lower idle clocks and power draw, since current machines cost ~$3k/month just sitting idle.

- **[Index Overflow & HEVC Decoder Performance](#chenyu-001263)**: Some index/packing code still uses 32-bit types and overflows when creating very large tensors (e.g., all parameters in one giant tensor); they want tests to catch this. Separately, the HEVC decoder is functionally working but slow, with `getitem` overhead inside `jit` identified as a key bottleneck.

- **[Mesa Backend & Image=1 Performance](#chrism-001405)**: Qualcomm/Mesa backend debugging suggests a possible Mesa register-allocation bug that appears when `no_locals` optimization is enabled; Chrism wants to merge current work while marking `no_locals` as broken and then focus on removing `image` from the dtype and implementing low-level image read/writes. Current `image=1` vision benchmark runs but is ~3× slower, so improving that path is a priority.

- **[CTypes Struct Bugs & Possible Replacement](#chrism-001631)**: Recent CTypes issues (notably `c_bool` bitfields being “totally broken” before a patch) have been addressed for reported cases, but Geohot pushes for a longer-term project to replace CTypes structs with a custom, faster, more stable abstraction that’s easier to reason about and can have better syntax/highlighting.

- **[FP8 Training Bounty & Torch Compatibility](#b1tg-001752)**: MMU faults in the training bounty runs are mostly fixed and some successful ATP runs exist, but coverage plateaus around 0.70–0.71 instead of the 0.72 target. FP8 changes for MI300 vs MI350 are being explored, and the team agrees behavior should generally match PyTorch unless there’s a strong, documented reason to diverge.

- **[USB Firmware Reverse Engineering, Schedule Cache, & Long-Term Vision](#geohot-002194)**: Geohot is using LLM agents to almost completely re-implement the USB chip firmware in clean C, with accurate register maps validated against manual RE. He plans to improve Python speed and extend schedule caching so more of the scheduling pipeline is reused. He also lays out a vision where future agents can fully reverse-engineer GPU/firmware stacks, enabling network-attached GPU “NAS-like” boxes and a Tinygrad world where the abstraction is at the tensor/model layer—making 1, 8, or 1000 GPUs look the same and unifying scheduling across all hierarchy levels.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=sc6cckdAXy8&t=0)]
Let's start with company update. Any company update?

##### **Geohot** [[00:00:05](https://www.youtube.com/watch?v=sc6cckdAXy8&t=5)]
Yeah, so we had a good revenue year this year. I'm looking at our Shopify sales. So our Shopify sales are up 22%. But we made 1.5 million last year, and we made 1.83 million this year. That's some TinyBox sales. And then in addition, we made $400,000 from AMD. So our revenue is up almost 50%.

##### **Geohot** [[00:00:33](https://www.youtube.com/watch?v=sc6cckdAXy8&t=33)]
Does that include the pros? That could be two things. Not anything we did with Commo, but that should be every box that we sold. Because we put all of that through Shopify, basically. Just to track it. Make sure we fulfill it and all that stuff.

##### **Chenyu** [[00:01:03](https://www.youtube.com/watch?v=sc6cckdAXy8&t=63)]
And also the RTX 6000 box seems to be selling pretty good.

##### **Geohot** [[00:01:10](https://www.youtube.com/watch?v=sc6cckdAXy8&t=70)]
Yeah, the RTX 6000 box is selling. I mean, when you look at the revenue from last year, it went heavily in August when we launched the TinyBox and finally got a check. We had a pretty bad first quarter of the year this year. But I'll post the

##### **Geohot** [[00:01:30](https://www.youtube.com/watch?v=sc6cckdAXy8&t=90)]
reads here as well. 700 000

##### **Flata** [[00:01:37](https://www.youtube.com/watch?v=sc6cckdAXy8&t=97)]
1.08 million

##### **Geohot** [[00:01:43](https://www.youtube.com/watch?v=sc6cckdAXy8&t=103)]
A very little salts deep selection. Like so many bots from over time, we've added or taken them on to our Amazon When I go to my Google search box, I see see who these matchers are with.

##### **Flata** [[00:01:52](https://www.youtube.com/watch?v=sc6cckdAXy8&t=112)]
See what I missed.

##### **Geohot** [[00:01:53](https://www.youtube.com/watch?v=sc6cckdAXy8&t=113)]
See what I missed, did not allem cooperate. Anything else? I think that's basically it. Oh, I see.

##### **Chenyu** [[00:02:15](https://www.youtube.com/watch?v=sc6cckdAXy8&t=135)]
Open to August last year?

##### **Geohot** [[00:02:18](https://www.youtube.com/watch?v=sc6cckdAXy8&t=138)]
Oh, that's when we launched?

##### **Geohot** [[00:02:19](https://www.youtube.com/watch?v=sc6cckdAXy8&t=139)]
I don't remember. Yeah, August last year was when we actually shipped all the tiny boxes. I mean, we didn't take the money until we actually shipped them. Like, launched them in April, but, you know, it took some amount of time. But yeah, no, I think, like, we didn't have anything for the first half of the year. Then when the green boxes came in stock, May, July was our top month. But it's been pretty stable. We've been making, like, 300 pay a month since July.

##### **Geohot** [[00:02:47](https://www.youtube.com/watch?v=sc6cckdAXy8&t=167)]
It's pretty good. No one buys the Red V2 box. Oh, we sold several Red V2 boxes. Yeah.

##### **Geohot** [[00:02:59](https://www.youtube.com/watch?v=sc6cckdAXy8&t=179)]
Red V2s are selling. Yeah, Red V2s are selling. We got our first, I think we got our first two of them shipped. It's a bigger hit than the Red box. I mean, I think the price just appeals to people. Had to sadly do a little bit of power limiting on that box. But it's a DP come overclocked. So it works that they're stock power, but it doesn't work that they're overclocked power. It'll brown out. Start getting DPs flowing off the bus. So we've got a lot of stuff. We capped the stock power. Everything's good. The Blackwell box is super stable. It's interesting. The fans on that card are different from, like, the normal TPU fans. They had to lay the cards out differently in the box. We put the three, like, the full vertical height of the Dunny box. Then we put the fourth card all the way on the other side. Still the hottest card. But they all stay below 80 now. So pretty happy with that. Yeah, I think we might have got our first

##### **Geohot** [[00:03:55](https://www.youtube.com/watch?v=sc6cckdAXy8&t=235)]
ship done. I'm not sure. I won't tell you. I know that a Redway 2 shipped. I'm not sure if any Blackwell shipped yet. Not this week. Chris, are you in the office? I am, yeah.

##### **Geohot** [[00:04:23](https://www.youtube.com/watch?v=sc6cckdAXy8&t=263)]
Well, welcome. Welcome to your first day. Yeah, thanks. I think you know what you're working on. I don't know if there are any questions or anything. But yeah, I told Julie to help you with any onboarding stuff you need.

##### **Flata** [[00:04:38](https://www.youtube.com/watch?v=sc6cckdAXy8&t=278)]
Cool.

##### **Geohot** [[00:04:43](https://www.youtube.com/watch?v=sc6cckdAXy8&t=283)]
Great. Okay. Let's move on to.. Oh, I did some update

##### **Chenyu** [[00:04:54](https://www.youtube.com/watch?v=sc6cckdAXy8&t=294)]
to the training loop.

##### **Chenyu** [[00:04:59](https://www.youtube.com/watch?v=sc6cckdAXy8&t=299)]
Take off my this just personally. Yeah. In your class? Keep it for MNES? except I didn't do the single big gradient thing.

##### **Geohot** [[00:05:34](https://www.youtube.com/watch?v=sc6cckdAXy8&t=334)]
Concerns at all about the JIT causing issues, if you run with debug equals one and JIT equals zero, you can see the schedule path and make sure that it's scheduling the same thing before the JIT actually kicks in. Because schedule path puts a hash out of the schedule. And if for some reason those schedules are changing, there's no way that this is gonna work. JIT might not still work, even if the schedules don't change, but if the schedule changes, the JIT definitely won't work. So if you're looking for ways to debug that. But yeah, hopefully the debug equals one output is pretty intuitive. Like it shows you your schedule and then it shows you the hash of that schedule and you can see like each step.

##### **Chenyu** [[00:06:14](https://www.youtube.com/watch?v=sc6cckdAXy8&t=374)]
Yeah, so anyway, I think if the BERT's wrong, I think the BERT's wrong is a good, test for correctness and I'll find a time to run the thing. I think if we have gradient accumulation, then depends on if I can test with flash attention that we can discuss later, we can have a B run training.

##### **Flata** [[00:06:41](https://www.youtube.com/watch?v=sc6cckdAXy8&t=401)]
Okay.

##### **Chenyu** [[00:06:46](https://www.youtube.com/watch?v=sc6cckdAXy8&t=406)]
Yeah, I will look into like the same or similar parameters for the B run. I will Day recruited a B run for quality and add some defaults. For now, those scripts was using a default from 405. So loc. " construocation avi." hyperparametrics are off.

##### **Geohot** [[00:07:04](https://www.youtube.com/watch?v=sc6cckdAXy8&t=424)]
I mean,it'd be nice to get a qualifying run if it's not too hard for AP as well. I mean,aslf only takes some time should be fun. Yeah, I mean, pretty, pretty fast, though, right? Like how fast are people getting it.

##### **Geohot** [[00:07:21](https://www.youtube.com/watch?v=sc6cckdAXy8&t=441)]
I guess we're only using one pack of zero and to 312, GPU now.

##### **Geohot** [[00:07:22](https://www.youtube.com/watch?v=sc6cckdAXy8&t=442)]
But I don't know if they have the runs with one machine. I can look at it later. But yeah.

##### **Chenyu** [[00:07:38](https://www.youtube.com/watch?v=sc6cckdAXy8&t=458)]
Also briefly consider if we want to merge FUSE opt-in and stuff like that. It's a little bit annoying if you shard things slightly differently. Because then I don't know if you want to group your gradients or parameters by how you sharded and try to concat light a big one or something like that.

##### **Geohot** [[00:08:06](https://www.youtube.com/watch?v=sc6cckdAXy8&t=486)]
The idea might just be to do it how I did it in gradient accumulate MNES. Reimplement the optimizer in our training here. Then we can update the optimizer later

##### **Geohot** [[00:08:17](https://www.youtube.com/watch?v=sc6cckdAXy8&t=497)]
once we know what it should look like. Yeah.

##### **Chenyu** [[00:08:24](https://www.youtube.com/watch?v=sc6cckdAXy8&t=504)]
So I think at some point, we want a functional update that take into your all the parameters you need and basically just assign to a new set of parameters. And we can all that function in the current state for one in the class. It's also a similar function, a functional API like that.

##### **Geohot** [[00:08:53](https://www.youtube.com/watch?v=sc6cckdAXy8&t=533)]
Yeah.

##### **Chenyu** [[00:08:54](https://www.youtube.com/watch?v=sc6cckdAXy8&t=534)]
But another thing you did is the one big gradient. And you just store their location and try to instead of having each parameters holding its gradient, have one big gradients for everything and update through that. That is a bit annoying if you shard your things differently on multi-GPU.

##### **Geohot** [[00:09:19](https://www.youtube.com/watch?v=sc6cckdAXy8&t=559)]
Yeah. We could actually even go as far. Do the sharding manually and just create sensors for the gradient on each CPU and then decide which to put in which place.

##### **Chenyu** [[00:09:29](https://www.youtube.com/watch?v=sc6cckdAXy8&t=569)]
Yeah. Yeah. I briefly consider. We'll probably think more about that when we are in a model pair row for the big LAMA.

##### **Geohot** [[00:09:38](https://www.youtube.com/watch?v=sc6cckdAXy8&t=578)]
Yeah. So I have the ML pair. LAMA 8B ends on MI350X in two hours. That's my thought. One MI350?

##### **Geohot** [[00:09:49](https://www.youtube.com/watch?v=sc6cckdAXy8&t=589)]
8 GPUs. Oh, 8 GPUs. So one machine.

##### **Flata** [[00:09:53](https://www.youtube.com/watch?v=sc6cckdAXy8&t=593)]
8 GPUs.

##### **Geohot** [[00:09:53](https://www.youtube.com/watch?v=sc6cckdAXy8&t=593)]
Oh, great. So hopefully we can get a similar time for that pretty soon. Great. OK. Let's move on to an important part, Ulysse.

##### **Chenyu** [[00:10:11](https://www.youtube.com/watch?v=sc6cckdAXy8&t=611)]
Let's flash attention.

##### **Wozeparrot** [[00:10:14](https://www.youtube.com/watch?v=sc6cckdAXy8&t=614)]
So I merged Flash Engine and Tensor.py last week. I also merged a bunch of prereqs for backwards pass. So backwards pass should land this week, I think, probably Wednesday, before Wednesday, because I'm flying out Thursday. So I'd like to get it in before Wednesday so we can start runs.

##### **Chenyu** [[00:10:36](https://www.youtube.com/watch?v=sc6cckdAXy8&t=636)]
Great. It should be good. You should be able to test with BERT, I think. We know how BERT behaves. And it also transfers faster. And you can run that on smaller machines. BERT only won't work. BERT only works. Does it really work with MI350?

##### **Geohot** [[00:10:52](https://www.youtube.com/watch?v=sc6cckdAXy8&t=652)]
It only works on MI350. It should work with at least MI300 as well.

##### **Geohot** [[00:10:58](https://www.youtube.com/watch?v=sc6cckdAXy8&t=658)]
Yeah.

##### **Geohot** [[00:10:59](https://www.youtube.com/watch?v=sc6cckdAXy8&t=659)]
Do that? Yeah. Because then we have four machines. We can try it on all four machines. I think that's pretty good. Like kick off some BERT runs on the 300.

##### **Chenyu** [[00:11:08](https://www.youtube.com/watch?v=sc6cckdAXy8&t=668)]
It's slightly annoying because we don't have disk. We don't have all the data on all the machines. I was trying very hard to find a machine to train my BERT.

##### **Geohot** [[00:11:19](https://www.youtube.com/watch?v=sc6cckdAXy8&t=679)]
Can we not copy it? Do we not have the physical disks? I know the 300 machine is a big writer. We can copy them to.

##### **Chenyu** [[00:11:25](https://www.youtube.com/watch?v=sc6cckdAXy8&t=685)]
Because we also want the big LAMA data set and a small LAMA data set and then a wiki data set.

##### **Geohot** [[00:11:34](https://www.youtube.com/watch?v=sc6cckdAXy8&t=694)]
So we have a bunch of those hard drives now. We might want to try to get some PCIe5 cards in the MI350 5x machine. We'll decide if you want to do that before you go, if we're going to have data problems.

##### **Wozeparrot** [[00:11:48](https://www.youtube.com/watch?v=sc6cckdAXy8&t=708)]
I remember we tried this. I know. And we could never get the cards to actually show up.

##### **Geohot** [[00:11:54](https://www.youtube.com/watch?v=sc6cckdAXy8&t=714)]
Oh, yeah. We tried a few things. So we tried those enclosures and they didn't work. Not sure if the problem was the enclosure or the problem was the.

##### **Wozeparrot** [[00:12:05](https://www.youtube.com/watch?v=sc6cckdAXy8&t=725)]
So I've also tried a RAID card by swapping out one of the network cards on the front of the machine. Did that work or no?

##### **Geohot** [[00:12:13](https://www.youtube.com/watch?v=sc6cckdAXy8&t=733)]
No.

##### **Geohot** [[00:12:15](https://www.youtube.com/watch?v=sc6cckdAXy8&t=735)]
OK, then I think we kind of get what we get. I mean, we can also. Is the data? It should be fast enough we can hit over the network, too.

##### **Geohot** [[00:12:25](https://www.youtube.com/watch?v=sc6cckdAXy8&t=745)]
Do you want to do like.

##### **Wozeparrot** [[00:12:28](https://www.youtube.com/watch?v=sc6cckdAXy8&t=748)]
There's not that much data. It's only like tokens.

##### **Geohot** [[00:12:35](https://www.youtube.com/watch?v=sc6cckdAXy8&t=755)]
Yeah, I mean, if we can fit it, we just need to make sure that all these machines can kick off trainers, like all the big machines.

##### **Geohot** [[00:12:42](https://www.youtube.com/watch?v=sc6cckdAXy8&t=762)]
They can fit all the data on the machine. Oh, great. Yeah, then let's just do that. Make sure it's. Just like R2. Yeah, I think it across the machine.

##### **Flata** [[00:12:53](https://www.youtube.com/watch?v=sc6cckdAXy8&t=773)]
Yeah.

##### **Geohot** [[00:12:56](https://www.youtube.com/watch?v=sc6cckdAXy8&t=776)]
Oh, yeah, so fast attention. Doing a successful.

##### **Wozeparrot** [[00:13:00](https://www.youtube.com/watch?v=sc6cckdAXy8&t=780)]
Good. If we want to fit more data, I can move the OS to. There's another NVME drive in the machine that we didn't put the OS on because for some reason it wasn't showing up before. But I got to show up by doing something. Forgot exactly what I did when I was testing this. But I can move the OS there and we can get it. And it's got another 4 terabytes.

##### **Geohot** [[00:13:23](https://www.youtube.com/watch?v=sc6cckdAXy8&t=803)]
Cool. The most important thing is that the machines do not break. I want to have broken machines. But yeah, whatever takes basically, we should be able to kick off BERT trainers, LLaMA 8 B trainers, and LLaMA 4 or 5 V trainers without a problem.

##### **Geohot** [[00:13:42](https://www.youtube.com/watch?v=sc6cckdAXy8&t=822)]
Wait, 405B? Where are we going to store these weights?

##### **Geohot** [[00:13:51](https://www.youtube.com/watch?v=sc6cckdAXy8&t=831)]
Yeah, I think a great goal for Zoom on Thursday would be to have a BERT running run succeed with class attention forward and backward, and then have all the machines be able to

##### **Geohot** [[00:14:03](https://www.youtube.com/watch?v=sc6cckdAXy8&t=843)]
replicate it. Sounds good. Anything else? Let's move on to this.

##### **Qazalin** [[00:14:26](https://www.youtube.com/watch?v=sc6cckdAXy8&t=866)]
I added PMCs to the UI. So if you run the physical studio, you'll see it. It's in the table. But the problem with these counters is that you don't really know why they are happening. So I am like next is I'm going to build it. I'm going to use a memory access visualizer to exactly show which threads access which parts of the buffer. And that way you can see if it's coalescent and stuff like that. I think HipKiddens has a nice visualizer for this. They didn't open source it, which is sad. But we have a reference picture of how it supposedly looks like.

##### **Geohot** [[00:15:11](https://www.youtube.com/watch?v=sc6cckdAXy8&t=911)]
We could probably message them on GPU mode. I'm sorry. It's probably in a really bad state. But I'm thinking about how to close a loop for you on this. And I think what you should work on is making the GEMM fast. Work on making the GEMM fast on the MI350s. We need that for LLaMA. And then you should work like close the loop between tooling and the GEMM. Like here's the GEMM. Make it faster. Oh, this would help with this tooling. Improve the tooling. So on and so forth. Keep that loop going. All right. There's no function for plate or flop. For the pointer toatalkay and LOLAMY we need two strings EL Let's see here. I love it. Let's see the Anima.

##### **Geohot** [[00:16:08](https://www.youtube.com/watch?v=sc6cckdAXy8&t=968)]
For a moment. If we have flash attention, if we have pay to plot map models, we're looking pretty good. Anything else for Riz?

##### **Qazalin** [[00:16:36](https://www.youtube.com/watch?v=sc6cckdAXy8&t=996)]
Chenyu, I know you asked about the rewrite index feature. I added in the branch, is it useful to merge more?

##### **Geohot** [[00:16:46](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1006)]
Oh, yes. I don't quite remember. I think it was useful. Let's discuss this later. I don't quite remember the details. Yeah. That's good.

##### **Chenyu** [[00:17:06](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1026)]
I want something like that just because there are rules that is very hard to find where it is used, especially in Riz. Especially if you're looking at a very giant rewrite. I think this is similar to the track rewrite status, maybe slightly different. But the idea is you want to see where some rules are used before you can decide if you want to move it or delete it.

##### **Geohot** [[00:17:36](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1056)]
Next, for the drivers. Yeah. So.

##### **Nimlgen** [[00:17:48](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1068)]
For the MI350 bug. It's actually fixed alone. Okay. So a lot of bugs in our on time but these ones, like in the frame of the loop managed to happen in. And. So, which when you made like, it's pretty strange, because like what you seen the mask. But it's like, It's almost the same address, like somewhere at the 48-bit address at the top of the memory address space. And it's actually from the instruction cache. And that's really, really strange. I mean, to my guess, maybe we have some stack corruption, but I'm not sure we use stacks at all because we don't do any function calls. I believe. And also, that's not really reproducible. So I think it happens in different function calls every time.

##### **Geohot** [[00:18:56](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1136)]
How's the AM driver going for 50?

##### **Nimlgen** [[00:19:00](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1140)]
Yeah, I'm working on it. So basically, it's fine. So yeah, I need to fix resets because they're also different to my 300.

##### **Geohot** [[00:19:20](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1160)]
That's the only..

##### **Flata** [[00:19:22](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1162)]
Yeah.

##### **Geohot** [[00:19:25](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1165)]
So that's the only part which is missing.

##### **Geohot** [[00:19:30](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1170)]
The issues, almost all the issues in RDNA 3 were caused by the thing that was trying to, like, the CSWR, like the contact wave state restore stuff. I wonder if it's possible that this.. Crash is coming from something like that. Like, do we have any of that sort of stuff enabled?

##### **Geohot** [[00:19:51](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1191)]
I believe we do.

##### **Nimlgen** [[00:19:53](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1193)]
But there is no mess.

##### **Geohot** [[00:19:56](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1196)]
Yeah, but even though there's no mess, anything.. It would not surprise me if that's the problem. Like, some old context is getting restored from something that's no longer in the instructions. And.. The PC is going to some weird.. I think it's a good address.

##### **Nimlgen** [[00:20:15](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1215)]
Yeah. Yeah, I can.. I can try to disable that.

##### **Geohot** [[00:20:20](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1220)]
But I think it would be better maybe just to go with the AM driver and then we just know exactly what's in there and what's not.

##### **Geohot** [[00:20:28](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1228)]
Yeah.

##### **Geohot** [[00:20:30](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1230)]
I don't like the idea of it being our own driver. I would also.. I would be so happy if the AM driver can lower the power draw of these things. It's costing us like $3,000 a month to keep these machines idle. And yeah, I looked into it a bit. It can't lower the mClock. So the mClock is always running at 2 gigahertz.

##### **Nimlgen** [[00:20:52](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1252)]
Yeah. I mean, it's possible in hardware. So yeah, we definitely can do this in AM.

##### **Flata** [[00:20:58](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1258)]
Yeah.

##### **Geohot** [[00:21:00](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1260)]
Good money.

##### **Chenyu** [[00:21:03](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1263)]
Another related thing is there are some overflows in index or the way we store numbers. That can happen. And we are seeing more of these with the bigger machine because if you have like 8B and store everything in one giant tensor, then that overflows.

##### **Geohot** [[00:21:29](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1289)]
Interesting. I thought our indexing stuff would deal with all of that. Yeah.

##### **Chenyu** [[00:21:35](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1295)]
So our indexing stuff deal with that. And hopefully the generative code is correct. But there are some places. I use the when we pack the numbers with the corresponding type, maybe the number is set to be like in32 or something like that. The Python pack and pack stuff. So I think the example is if you just create one giant, I don't know, like an pickup tensor and that will fail.

##### **Geohot** [[00:22:11](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1331)]
But if you just create one giant, it will fail. It'd be great. Let's get some testing for that. We definitely don't want those kind of crashes. And how is the HVAC decoder coming?

##### **Nimlgen** [[00:22:30](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1350)]
I mean, it's cheated, but it's not very fast because the get item still takes a lot of time inside cheat. Where's the add to the get? Well, it's the X pourquoi I need to deploy Y, theim baik extreme, the pull?

##### **Geohot** [[00:22:52](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1372)]
Wellalart on your iPhone. So I think the X where Y to Nίν no esso no ç against plus AND between the and

##### **Flata** [[00:22:57](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1377)]
That's what it did it, right?

##### **Geohot** [[00:22:58](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1378)]
It's a rational consequence because we're laying that over to so many companies. But let's explore the other one, the door, liquidity if we're seeing aains one Minions

##### **Flata** [[00:23:07](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1387)]
or 

##### **Geohot** [[00:23:09](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1389)]
That was good. Anything else for drivers? No. Move on to Mesa.

##### **Chrism** [[00:23:25](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1405)]
Yeah. I'm not totally sure what's going on here. I mean, I found some bugs, but at this point, I'm starting to think there might be a bug in Mesa pertaining to register allocation. I'm not totally sure what's going on. But it seems to work without a no locals set. So to my understanding, the no locals optimization, it's a strict subset of the stuff that BEAM can discover. I don't know if that's correct, but I think.

##### **Geohot** [[00:24:00](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1440)]
Is that correct? I mean, the thing that allows you to do is to do the same thing. We have some fractional stuff, and that's why the no locals is fast. No locals. OK, so no locals does two things.

##### **Geohot** [[00:24:16](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1456)]
So you can read two different functions in OpenCL, one that reads the group work ID and one that reads the global work ID. The global work ID is the group times the number of locals plus the local. So no locals is a function that will run with any size locals, but it's fixed. So you can do a search in there that'll search over all the possible locals to see what's fast. The main advantage you get for this over the other path, Qualcomm allows for fractional global. So Qualcomm, the locals do not have to divide the global size evenly. That makes things faster. But if it doesn't work, if no locals doesn't work, that's fine. It's not that much lower. We're talking about like 5%, 10% here.

##### **Chrism** [[00:25:06](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1506)]
OK, yeah. Anyway, I'll look at it a little bit longer. But at this point, I feel like the bug here is actually something in Mesa. Because it's just like I fixed some stuff, but I've been looking at the output code, and it just seems like it's clobbering. I'd have to double check. I want to try and find a minimal reproduction so I can look through the code and make sure I'm not confusing myself. But it really does look like it's clobbering its own code.

##### **Flata** [[00:25:33](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1533)]
Yeah.

##### **Chrism** [[00:25:34](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1534)]
It's just like it's indexes into the image load. Anyway, I don't know. The Qualcomm code, definitely it all works without image support. But that's to be expected.

##### **Geohot** [[00:25:46](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1546)]
We really shouldn't be spending time on Mesa bugs. I think the next project here is to get image removed from D type and get the low level imagery rights to work, be that with the Qualcomm back end or the Mesa back end. It doesn't really matter.

##### **Chrism** [[00:25:58](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1558)]
Yeah, I agree. So yeah, yeah, that makes sense. I think I kind of just want to merge this in the state that it's in and maybe just say, no, the local doesn't work. And then I can start working on the real interesting project, which is trying to get images to work properly or without the image equals two.

##### **Chenyu** [[00:26:18](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1578)]
If I merge the image equals to one vision model to the benchmark, I think now it's just

##### **Geohot** [[00:26:27](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1587)]
3x slower. That's good. We need to make image equals one.

##### **Flata** [[00:26:35](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1595)]
Yeah.

##### **Chenyu** [[00:26:43](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1603)]
I also probably will want to test that with BEAM to see if it's just we do one less upcast and it's slow, something like that.

##### **Geohot** [[00:26:54](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1614)]
But anyway, making image equals to one, that would be great.

##### **Chenyu** [[00:26:59](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1619)]
Yeah. OK. Anything else for you?

##### **Chenyu** [[00:27:05](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1625)]
Oh, can you briefly talk about the state of C-type bugs, like what to use, what not to use?

##### **Chrism** [[00:27:11](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1631)]
Yeah. I think everything is fine. I think I fixed everything that people complained about in the bug reports channel. But yeah, the bug is with, or the most recent bug that I encountered is with C underscore bool. If you have any C underscore bool, you can fix it. But if you have any C underscore bool with a bit field, it's just totally broken. It just doesn't work at all. So but I add, there's a patch for that now. So our structure implementation deals with that. So it shouldn't cause any issues. But if you encounter more bugs, let me know and I'll fix them.

##### **Geohot** [[00:27:58](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1678)]
I really like the project. It's just not using C-type structure and just replacing that with something else. C-type structure is slow, undocumented, and changes. And that's just manually managing the field. I'm very supportive of that project, too.

##### **Chrism** [[00:28:13](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1693)]
Yeah, that would be, that's also something I want to do. Yeah. Yeah, I don't know if that's as high priority right now. But yeah, definitely, it would be nice to do and also probably get syntax highlighting working and just a better syntax in general for defining these structures.

##### **Geohot** [[00:28:31](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1711)]
Yeah, I mean, I think the priority should be determined by how annoying the bugs are. If the bugs aren't annoying you, then it can wait. If the bugs are annoying you, then be like, well, instead of pouring more effort into fixing these bugs, just rewrite it differently. But if the bugs aren't annoying you, then it can wait.

##### **Geohot** [[00:28:42](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1722)]
Yeah, I think if I encounter too many bugs, I'll, yeah. Sounds good.

##### **Chenyu** [[00:28:53](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1733)]
Let's move on to other bounties. We can start with B1TG.

##### **Chenyu** [[00:28:58](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1738)]
I saw you're training wrong. Yeah. How are things going?

##### **B1tg** [[00:29:06](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1746)]
Hello.

##### **Chenyu** [[00:29:08](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1748)]
Hello.

##### **B1tg** [[00:29:12](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1752)]
The MMU fault basically fixed by new change. It can still happen, but with more probability. I have few success atp runs. Now the problem is it can't coverage. And do you have any? The coverage can now be 0.7. But it can't reach the 0.72. So I was planning to adjust the fp layer a bit and also try the block scale.

##### **Chenyu** [[00:30:11](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1811)]
I remember last week you talked about, last week you talked about you want to use fp8 or not using fp8. Let's put it in VFX. Well, obviously it's not maxed out.

##### **Flata** [[00:30:32](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1832)]
It's designed to be very nice.

##### **Chenyu** [[00:30:33](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1833)]
And if it's too dense, I will then use fp8.

##### **Flata** [[00:30:36](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1836)]
So in this case the fulfull collaborated with this new feature. And the bug, I myself have been info. And come back and you're uncertainly. ##### **B1tg** [[00:30:37](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1837)]
It didn't influence the coverage or language.

##### **Flata** [[00:30:46](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1846)]
I'd also been used to there's weird GPS bar now. ##### **B1tg** [[00:30:48](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1848)]
It didn't really add ideally bad value to yourstrue as you were missing out So..

##### **Chenyu** [[00:31:01](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1861)]
Okay, I think it would be useful if we just clear some of your experimentation rounds in the BERT channel or something like that. Because I also don't know anything about the day channel. No.

##### **B1tg** [[00:31:23](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1883)]
Okay, I will put something this week. And also, when I wait for the counter fix, I add the FP base spot for the.. MI300. The FP8's.. Implement is different from.. MI300 and.. MI3.. MI350. We want that one.

##### **Chenyu** [[00:32:17](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1937)]
I don't know in what way they are different. It's just.. I told you that different handsets are different. And it's just a completely different thing we need to discuss. Like what's good for that. And what's not good for that. I know for how we are using it. We talked about a few of that. But.. I don't know, it might be like..

##### **Flata** [[00:32:43](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1963)]
Different.

##### **Chenyu** [[00:32:44](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1964)]
Because.. Everyone uses slightly different. You see? So..

##### **B1tg** [[00:32:51](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1971)]
So I guess.. Basically, we want to match the behavior with touch. PY touch.

##### **Chenyu** [[00:33:05](https://www.youtube.com/watch?v=sc6cckdAXy8&t=1985)]
I think generally for torch.. Unless we have a very good reason not to match.. We should match their behavior. There are a few cases that we clearly know torch behaves weirdly. And they document this in their code for some legacy issues. Other than that, I think it's a good starting point.

##### **Flata** [[00:33:28](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2008)]
To..

##### **Chenyu** [[00:33:31](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2011)]
Have the behavior match torch.

##### **B1tg** [[00:33:37](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2017)]
Okay, I will put a PR later.

##### **Chenyu** [[00:33:42](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2022)]
Yeah, just.. Also feel free to.. Feel free to open issue saying.. This is a current behavior. It doesn't match. And it should or it shouldn't. Adding some context helps here. Exciting. Yeah, I think we.. If we can get a PA training.. It also helps a lot with LLaMA.

##### **Flata** [[00:34:09](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2049)]
Yeah, I think we.. Yeah, yeah.. Soon.

##### **Chenyu** [[00:34:18](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2058)]
You.. Ooh.. Oh,�0w 0n0w. I have to we see, help me hear a comment.. Hey, ding here. Hey, ngresum ngrya?

##### **Flata** [[00:34:26](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2066)]
Hi, it's Thi Bo Thanh. If you've been working for Fiat Towers last year? Hey, am into Goss Mattus anyone publicizing that thing yet? Yeah. I've decided I'll go get more suppliers, if they can. I think we have a number here, the conoscypa list. Do we have İşte? based on the random number generator. And they were using the typical PyTorch data loader. So we just have to make sure that's consistent with my implementation for the Flux version for TinyGrad.

##### **Geohot** [[00:34:57](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2097)]
Yeah, I don't have things to say about this. I think generally the idea is..

##### **Chenyu** [[00:35:08](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2108)]
So our LLaMA implementation, I know, was pretty much copy what the reference was doing. Maybe with the caveat that the reference also used a lot of weird flags. So who really knows what is really being used? But the idea is with MLPerf, it's important to know if they have a specific order for how you load the data. Do you reshuffle the data? Do you shuffle within batch? And if so, how much is your shuffle window and things like that? I think as long as loads are well understood from the reference, our real implementation, as long as they match that in spirit, we should be good.

##### **Geohot** [[00:35:58](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2158)]
Okay, sounds good.

##### **Chenyu** [[00:36:00](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2160)]
Yeah, and I mean, assuming our model conversions are the same as the data, it's not dependent on the shuffle order. Then even if we use a wrong one, it should be fairly straightforward to just use the correct one.

##### **Geohot** [[00:36:15](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2175)]
Our training shouldn't depend on the order anyway.

##### **Chenyu** [[00:36:24](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2184)]
Okay, what else do we have for other monkeys?

##### **Geohot** [[00:36:30](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2190)]
Oh, I've been working on, not that.

##### **Geohot** [[00:36:34](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2194)]
That's just in my clipboard. On a complete reimplementation of the USB chip firmware. It's amazing how good some of these agents have gotten. You have to really work hard to keep them on track and prevent them from doing dumb stuff. And you have to really stay on top of them. But this is almost a complete reverse engineering of the firmware that's on the USB chip. So this is finally going to enable the speed for Comma to start using this chip. And I've been impressed by like, you can read the register map in there. It's so much better than any other register map we've ever had from the chip. And it all actually does seem pretty correct. I've checked it with the stuff that I've manually reverse engineered. This is the main thing that I've been working on. I'm going to finish it up this week. I'm also going to work on, I'm going to work on Python speed. And I'm going to work on improving schedule cache. So schedule cache can actually do a lot more than what it's currently doing. We're only schedule caching like one little part of the scheduling, but you could schedule cache all the way through. I'm also going to look into that 8-pack thing and see why the bits go slow. Think about how to.. Schedule cache should get you 50% of the chip behavior for absolute free. So, you know, I mean, the whole project of making TinyGrad easier to use. That's..

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2284)]
I'll be working on that and working on the.. SP firmware. Sounds good. Oh, is the whisper thing ready for review? I feel like it's been here forever. I don't know. It's been here forever. I don't know. I don't know. I also don't see the upgrade from the Winograd. I don't know what happened there.

##### **Geohot** [[00:39:01](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2341)]
I'm also going to merge this thing bumping on it. 1.19

##### **Geohot** [[00:39:08](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2348)]
is there any reason not to?

##### **Chenyu** [[00:39:12](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2352)]
the reason might be why not do 1.20?

##### **Geohot** [[00:39:16](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2356)]
yeah we could do 1.20 as well but

##### **Geohot** [[00:39:21](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2361)]
sure

##### **Geohot** [[00:39:21](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2361)]
if it looks good

##### **Geohot** [[00:39:29](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2369)]
I probably should have tested it with the I'll revert it if the comma stuff breaks okay I don't see any other funky

##### **Chenyu** [[00:39:43](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2383)]
anything else for this meeting?

##### **Geohot** [[00:39:46](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2386)]
we have to get them all there

##### **Geohot** [[00:39:48](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2388)]
I don't really think it's much else again I'll say overall I'm very excited on at how good these LLM agents have gotten at reverse engineering and they're not quite there yet but I can easily see a world in two or three years where I can hand it something like the AMD mech firmware and be like re-implement this and see and it will reverse engineer everything about the chip even from nothing there'll be register maps there'll be driver abstractions that perfectly match function for function the real ones but re-implemented in very readable C that's probably even more readable than the original repository so the era of companies being able to keep hardware secret just releasing binary logs for firmware is coming to a close and this is extremely exciting for all the stuff that we'll be able to make these AMD GPUs do all the stuff we'll be able to make these chips do I think that this is the pinnacle of what LLMs themselves can do is just cut through all of this noise that's in these firmware things and we can build things that look like tiny grids that just are the true essence of the code without all of this abstracted nonsense I posted that Twitter post about the USB not the USB the GPUs over the network I think that's eventually where we want to go I can see that actually happening in two years I can totally see us selling a network attached NAS like NAS like network attached cards like that and I think that's totally true I think that's from the perspective of what people really want is the abstraction that they want is the abstraction at the at the model layer or at the tensor layer they do not want the abstraction at the SIROV of the GPU like that whole abstraction stack is wrong the right abstraction stack is tensor across there should be no distinction between one GPU eight GPUs a thousand GPUs all just the same problem at every level of the hierarchy and yeah that's the that's the tinygrad dream like all of that every level of a hierarchy use the same code you can start to see this now between the difference between the big graph and the small graph are getting smaller and smaller and smaller I can almost see separating the small graph into pieces based on where you have barriers like barrier is the same thing as bufferize not exactly but like unify all of this and then schedule hierarchically at all the different layers

##### **Geohot** [[00:43:04](https://www.youtube.com/watch?v=sc6cckdAXy8&t=2584)]
it's the same problem repeated every time great okay that concludes this meeting thanks everyone see you next week thanks bye
