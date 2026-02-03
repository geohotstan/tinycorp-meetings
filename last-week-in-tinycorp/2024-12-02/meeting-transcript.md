# 2024-12-02 Meeting

### Meeting Agenda

**Time:** 8pm Hong Kong time (next week will be 9.30 AM west coast time, PST?)
- Company update, new employee!
- Delete lazy
- Block
- Speed regressions, pad rewrite
- Driver and hcq cleanups
- Bounties (tensor cores, tar_extract, onnx, qwq)

### Audio

[Recording](https://drive.google.com/file/d/1I6wHnyNvhPull0kkL6tkx8LiBrtxxFO7/view?usp=sharing)

### Chapters

- **00:00:00 Introductions and NEW TINYCORP EMPLOYEE!!!** New intern Wpmed joins for WebGPU work.

- **00:01:30 Geohot's WebGPU Plan** How to prevent "enshittification" of the AI internet.

- **00:05:50 WebGPU Benchmarks** Plans for WebGPU performance tracking.

- **00:08:02 Testing and Performance Tracking** Setting up browser performance tests.

- **00:10:27 LazyBuffer Deletion Challenges** Addressing state sync and JIT issues.

- **00:16:24 Block Linearization Improvements** New block approach.

- **00:17:36 Speed Regression Investigations** Investigating Stable Diffusion slowdowns.

- **00:23:41 Cloud Preparation** Updates on cloud readiness.

- **00:31:34 Tinygrad Cloud Beta Plans** Beta launch details for contributors.

- **00:36:11 TensorCore Updates** TensorCore swizzling bounty claimed by Ignaciosica.

- **00:40:03 Tar Extract Utility** Tensor file extraction for cloud loading.

- **00:42:18 RetinaNet and QwQ Training** Updates on RetinaNet and QwQ progress.

- **00:44:36 MTL Compiler** Discussion about Metal compilation.

- **00:50:50 WGPU Compatibility Issues** Debugging WebGPU timeout issues.

### Transcript

**Chenyu** [00:00:00]
Should we get started?

**Geohot** [00:00:04]
Sounds good.

**Chenyu** [00:00:07]
You can have the first one.

**Geohot** [00:00:10]
Yeah, so Wpmed has joined us as an intern to work on WebGPU stuff, if you'd like to introduce yourself.

**Wpmed** [00:00:21]
Yeah, sure.
Yeah, thanks for having me on board.
I'm Ahmed Harmouche from Hungary.
I've been working mainly in the mobile app development space doing image processing on iOS and Android.
I co-founded Vimage app.
It's a photo animation application with around 10 million downloads in the Play Store.
Then after five years or so, I left Vimage to work at Toptal doing freelancing.
And while doing freelancing work at Toptal, I started picking up Tinygrad, started contributing to it, mainly for WebGPU stuff.
And basically after getting WebGPU merge, we talked with George and we discussed this internship position and I was like, okay, let's try it.
So that's pretty much it.

**Geohot** [00:01:30]
Cool.
Yeah, our goal is to make some very usable web apps.
I want Tinygrad to be the go-to framework for deploying things to browsers.
I think that most neural networks that people run are going to
either be cloud or in browsers, right?
Like it has to be in browser, whether the compute is local or whether the compute is remote.
I think a key advantage that all the local things have over the remote ones is that once the site's deployed, it just works, right?
The problem with the remote one is, well, you have to come up with a business model and you're always going to make it shittier, right?
And [enshittification](https://en.wikipedia.org/wiki/Enshittification) comes to everything that has a cloud-based business model.
Think of the Claude or Openai limits.
And I still believe these companies may be losing money, but it doesn't even matter if they're losing money.
They could be making more money if they rate limit you harder.
They could be making more money if they add advertisements.
They could be making more money if they artificially slow it down so that you submit less requests.
Every single thing where the application is hosted on a server, the server's incentives are not aligned with yours.
So I hope that by making Tinygrad, by making it really easy in Tinygrad to push things to the web in such a way that edge devices can run it, be that a laptop or be that a phone, we can, you know,
work toward our mission of commoditizing the petaflop.
We do not want the petaflops.
Look, the only reason that I started this company, the only reason that I'm here is to fight against the basic.. I don't want AI to suck the way the internet did.
And I think in order to make.. I think the key to making AI not suck the way.. The reason I think the internet sucks is because it's so difficult to
stand up like a database right like imagine you wanted to build decentralized google
You can't, right?
Like Google has so many advantages to being centralized, even to all this tooling.
Okay, I want to stand it up.
I'm going to get AWS boxes.
I'm going to have Docker containers.
Oh, now I need a DevOps guy.
Oh, now I'm going to use this, right?
You're just getting sucked into funnels everywhere to build out these incredibly complex systems.
But if we can make the system simple and enshitification will not happen in the AI space.
And yeah, I think that like, I just posted on Twitter about it.
Someone suggested we do transcription, we do Whisper.
I think Whisper is a great application of putting it in the browser, right?
Because the thing about AI is there's gonna be a thing where it's just good enough, right?
90% of your requests can be handled by cheap, simple models.
And if that holds,
then we're in for a great positive change to the internet.
So yeah, that's why we're excited about WebGPU.
That's what we want to do.
We want to both host, make common models, not host them.
We're not hosting shit.
It's all hosted by HuggingFace and GitHub, but make it easy to deploy models to the web in hopes that enshitification is prevented.
And then that's from the consumer side.
And then from the server side,
we are going to launch our first test cloud, hopefully in a month or two.
And that's how I'd like to see training and stuff be done, right?
If we can..
Again, so many companies are looking to rent-seek.
So many companies, you already see the wheels turning for the rent-seeking.
It's, oh, okay, how do we value add on top of LLMs?
Oh, how do we, oh, we can offer a hosted infrastructure solution.
No, no, no, no, no, no.
Not hosting any of that shit.
I'm going to open source all of it.
And then it's going to be a race to the bottom to sell petaflops for dirt cheap for training.
And that's how we make the internet not, you know, the AI internet not shitty like the first time.
But eh, we'll see if it works.
So that's why we're excited about web.
Sounds good.
Train in Tinygrad.
Train in Tinygrad on our cloud.
Ship to the edge.
Done.

**Chenyu** [00:05:50]
Yeah.
I was thinking we would probably want to add some benchmark of WebGPU.
Is a second Mac ever set up?
If I send it to Mac, does it go to a different runner now?

**Geohot** [00:06:04]
It should, yeah.
The second mac would totally work.
We can check if it doesn't, but yeah, it should be fine.

**Chenyu** [00:06:12]
I think it's a good idea now we have someone looking at WebGPU.
It's good to track certain performance on it, especially if we want to.

**Wpmed** [00:06:20]
Yeah, I'm also interested in WebGPU performance, like how it relates to Metal, how much overhead it adds, for example, to Metal.
I see that the wgpu Python package we're using currently, so it's a wraparound of wgpu native, it's a Rust library.
I see that it's slower than Chrome's WebGPU implementation, so I'm also really interested in
in building a sort of auto-gen style bindings for Dawn and using that instead of wgpu.
But first, I have to look into exactly how much faster Dawn is.
Or actually, first, let's just learn about wgpu that we currently have and then see how much Dawn is faster.

**Geohot** [00:07:21]
Can we just run like Selenium or Puppeteer or something on the second Mac and run things straight up on the browser?

**Wpmed** [00:07:28]
Yeah, yeah, we can do that.
Actually, we do this puppeteer style of testing for EfficientNet.
So when WebGPU tests run, there is an EfficientNet build and it tests it in the browser.
So we can do stuff like that.

**Geohot** [00:07:42]
So we have a separate CI we call Benchmark CI.
You see it.
It's visible to everybody, but only people with push access to the repo can actually push things to it.
But yeah, we can use the second Mac, and we can stand up.
It's an M2 Macs, so it can totally run Stable Diffusion in the browser.
So we'll run that through Puppeteer, and then we can track that performance.

**Wpmed** [00:08:02]
Yeah, that sounds good.

**Geohot** [00:08:05]
Is that what you're thinking, Chenyu?

**Chenyu** [00:08:07]
Oh yeah, something like that.
So we benchmark what we want to offer to the users.

**Geohot** [00:08:16]
Sounds good.

**Chenyu** [00:08:17]
Cool.
Okay.
Since everyone is more or less touching delete lazy, let's start with delete lazy, Qazalin.

**Qazalin** [00:08:27]
Yeah.
TestOps passes.
It's green.
I spent an absurdly long amount of time
before realizing that the memory planner changes the buffers of the ExecItem.
And it looks like JIT does it as well.
So I think one of the last fundamental problems with it is that the state is getting out of sync because buffers are changing across the runtime.
I don't know how to solve this yet, but JIT right now isn't passing because of this.

**Geohot** [00:08:55]
I see what you're saying.
Yeah, I saw that image change too.
Unfortunately, if you mark the UOp mutable, you just lose like 5% of performance because mutable hooks all of the accesses.
It's just Python that hooks all the accesses, unfortunately, if you do frozen equals true.

**Chenyu** [00:09:12]
You say no frozen is faster or frozen is faster?

**Geohot** [00:09:17]
No frozen is faster.
frozen is it's all emulated

**Chenyu** [00:09:23]
Yeah frozen is emulated by python, so that's slow

**Geohot** [00:09:26]
yeah yeah um but yeah no i uh i see what you're saying about how like yeah the buffers change for the JIT i updated the JIT test to actually test the JIT properly

**Qazalin** [00:09:40]
Oh, it's proper.
Everything is proper in the test JIT.
My diff isn't proper.
It's basically like expecting buffers to be different, and then you change the buffers, but you don't change the reference UOps buffers.
So that buffer ends up existing.
So you have like two different places where the state is getting out of sync.
The whole reason why we have this concept is because UOps are immutable and you can't have buffer on the UOp itself.
So you need to somehow, like when you update the buffer later, you need to actually update the map as well.
I have a hack for the memory planner.
It's ugly, but like I think these two last things, as you mentioned, the image one.
The last ones are going to be a little ugly.
I'm going to see how I can solve them.
But those are pretty much it.
I'm pretty happy with the diff, negative 100 lines.

**Geohot** [00:10:39]
Yeah, well, we have to get this in.
Everyone needs to build on top of it.

**Qazalin** [00:10:46]
How do you think we can solve the state getting out of sync problem?

**Geohot** [00:10:51]
I'll have to look more into it.
I'm not exactly sure.
I can't just come up with something right now.

**Chenyu** [00:10:58]
If there's a property that you cannot derive again from your updated UOp, then the only way I see is every time you update this underlying UOp, you also underline the metadata that's dig or whichever digs it.
Like associate with it and update both.

**Geohot** [00:11:19]
Yeah, I see what you're doing in the memory planner.
And you could just make that a function and call that every once in a while.
I'm fine with, let's just get this merged, even if that's what it did.
Loop through all the new ExecItems, see if anything updated, and then update them.
Every time you run ExecItems, that's fine.

**Qazalin** [00:11:48]
I guess that's the only solution, yeah.
for image um I don't know

**Geohot** [00:11:59]
uh the image mutability thing?

**Qazalin** [00:12:02]
yeah

**Geohot** [00:12:05]
yeah I don't know about that either uh I can I can try to look at that one um I mean yeah I that shouldn't have gotten in there we were changing the
That's actually changing a UOp.
Oh no, it's changing a LazyBuffer.
Oh.
Actually, you know what we can do?
The only reason, why do we ever have to do that image fixup?
It's just for stores, right?

**Qazalin** [00:12:46]
Yeah.

**Geohot** [00:12:49]
You know, we might be able to..
OpenCL supports Atomics.
If OpenCL supports Atomics we could do basically the same trick we do in WebGPU and then just not need that whole thing.

**Chenyu** [00:13:16]
OK, we will look into this.
This is the last few blocker.
Everyone is excited about this.
We will get it merged first.

**Geohot** [00:13:24]
Work on the other thing.
I'll take the image thing.

**Qazalin** [00:13:28]
OK, I'll take the JIT.

**Geohot** [00:13:30]
Cool.

**Chenyu** [00:13:38]
We will get this merged soon.
We're going to claim our 100 lines.
Great.

**Geohot** [00:13:44]
I already have plans to waste them.

**Chenyu** [00:13:48]
Let's go to block because you already added 60 lines to it.

**Geohot** [00:13:55]
Yeah, but they're pretty lines.
I got rid of the minus 10,000.

**Chenyu** [00:14:02]
That's very good, yes.
And plus 1 million.

**Geohot** [00:14:08]
Yeah, yeah, yeah.
It's all correct now.

**Chenyu** [00:14:14]
Do you want to briefly go through what it is?
What's new?
How do you do it?
What do you like future TODOs for it?

**Geohot** [00:14:23]
Yeah.
So if you go to, it's in linearize.py.
If you go to linearize.py and you look at, you can really see it well with VIZ=1.
So the linearizer now is no longer a,
handwritten Python outside thing.
It's actually just a bunch of graph rewrites.
The key thing that it separates is like, so it's almost impossible to make all topological sorts of the graph valid because you have loops.
So now I've broken it into like two stages.
And these two, as long as you have the two stages correct, all topological sorts are correct.
And it's really key that all of them are.
So you can have,
First, I group all ops into blocks.
And then I stack blocks on top of each other based on what has to go inside a loop and what can't go in an if and what has to go in an if.
It's this two-stage algorithm that first puts all the ops into blocks and then stacks all the blocks together into one long list.
And each of those individual toposorts can be completely..
Well, the inside the block one can be completely arbitrary.
The stacking the blocks have a few rules.
But yeah, so I think this opens the door for sensible,
and really what I should write, maybe we'll do this tomorrow, is write a fuzz test to check all permutations inside blocks and make sure they're correct.
So I have two things to write tomorrow.
Make the blocks bigger and check all toposorts inside the block and make sure it's correct.
And we tried this like in the past, fuzzing the toposorts, and they never worked.
But now I think we have a methodological way to do it.
So that's why we spent 60 lines.

**Chenyu** [00:16:24]
Let's see.
Did it fix the, I think we have few in cstyles, there's variable scope issue causing rendering bug.
Did that fix?

**Geohot** [00:16:36]
Are there tests for it?
All the tests pass.

**Chenyu** [00:16:41]
OK.

**Geohot** [00:16:42]
Oh, are there some of the linearizer failures?

**Chenyu** [00:16:46]
Yeah.

**Geohot** [00:16:48]
I can look at those tomorrow.
But as far as I know, all the same linearizers failed.

**Chenyu** [00:16:53]
I see.
OK.

**Geohot** [00:16:56]
Yeah, I see.
So like, did test value 53?
Yeah, a little bit.
Sounds good.
Cool.

**Chenyu** [00:17:09]
The next item.
So speed regressions.
So I will look into this, I think.
I don't see ResNet diff, and you said stable diffusion on Mac is worse.
I see.
So I just opened stats now.
I see unjitted got slower again.

**Geohot** [00:17:36]
Oh, I don't know about unjitted, but stable diffusion and stable diffusion.
Oh, which caused that?
Buffer number?

**Qazalin** [00:17:42]
Buffer number, yeah.

**Geohot** [00:17:45]
OK.
Yeah, I don't think, yeah, I didn't do the unjitted one, but I did the jitted one.
If you look at stable diffusion on math, that's slower.
So did CIFAR on math.

**Chenyu** [00:17:59]
CIFAR, yeah, it's probably a similar thing.

**Geohot** [00:18:03]
ResNet got slower, but only on red.
But comma got faster.

**Chenyu** [00:18:09]
That's really good.
Do you know why it's just better order as before?
OK.

**Geohot** [00:18:14]
No, I know explicitly why.
So the old ordering used to load the biases before the conv loop and then add the biases after the loop.
So it would put the loads before the loop.
And you don't want to do this because it would waste all those registers while your loop's going.

**Chenyu** [00:18:32]
It's more than one millisecond.

**Geohot** [00:18:36]
Yeah, it's locality.
It's a registered locality.
But also, there's some regressions in red and Mac, but there's no regressions in green.
That's just because NVIDIA has a better compiler.

**Chenyu** [00:18:53]
Yeah, so for some reason, training ResNet on red was hanging and crashing.
It's doing weird stuff.
Prior to, I don't know if it's specifically this block change, but something else, it was crashing and not finishing.
without resetting the GPU itself or something.
But it's fixed now on master.
But we have seen this before.
It looks like just some random compiler issues.
I don't really know.
So every time, as long as green is running and trending and red is crashing, I don't really care at this point.
But it's fixed now, so that's good.
I also plan to look at what's happening for the versus theoretical.
I feel after introducing that test, it's not really that helpful.
We just know things got slower.
I will see what I can do to make that test more beneficial than just every time we hit it, we lower the number or something.
Oh, and I was testing with several condition rewrite rules with where.
So there is one that I was interested.
I want to merge ALU for branches if the gate is the same.
I think that's the case.
And I want to do this at least if one branch are both const.
So you can const load that branch, such that your ALU count is not larger than before.
Because if both of your branches are some buffers, then your total ALU can be more, because I would need to do ALU for both.
But if at least one is both consts and can be folded, then you keep it the same, and it's potentially faster.
There's another one that is if your gate has a negation to it, then you can remove that negation and just flip your branches.
So this is kind of a canonicalization to your gate and can make the previous merge faster.
Then I started to do that.
Then I started to hit.
We have several places that we like arange folding, loop folding is one of it that we check.
It needs to be like in a negation form.
That's kind of annoying.
I was thinking about how to do that.
I'm interested in this, because there are a few cases that I know things can be fused to a lot simpler.
Probably also working on this.

**Geohot** [00:21:53]
The UPat.any syntax is pretty good if you want to do the negation on negation form now.
The arange stuff is way more tangible than ever before.
But yeah, ideally, there's some much better way to approach this at a higher level.

**Chenyu** [00:22:02]
Yeah, I'll probably just also check that.

**Geohot** [00:22:06]
Yeah, I think eventually, longer term, we're going to move to this concept of optional rewrite rules and required rewrite rules.

**Chenyu** [00:22:23]
Yes, I really want this.

**Geohot** [00:22:26]
Yes, yes.
And you can kind of start on it now, and then eventually we're just going to put intelligence search on do you want to do the rules or not.
If rules can be applied different ways, you can include a number with that search.
There's a lot of possibilities here.

**Chenyu** [00:22:44]
Yeah, there are also, yeah, it's another kind of,
uh what we do in kernels up up now but that applies at the kernel level and I guess we have the blocks in some sense it's like applying to all the codes in that kernel

**Geohot** [00:23:00]
So my big project back in san diego I had two things to work on san diego uh one is getting the cloud up and the other is rewriting kernel.py
Yeah, pad is different, but upcasts and unrolls and groups are all rewrite rules.
Yes, I think.
And then those rewrite rules, that's when we want to start introducing this concept of optional versus required rewrite rules, because the OPOPT is basically an optional rewrite rule.

**Chenyu** [00:23:41]
Yes, yes, yes.
Anything you put as optional, you can potentially search for that.

**Geohot** [00:23:48]
Yeah.

**Chenyu** [00:23:50]
Anything that can be searched will start with a heuristic like hand code optimization.

**Geohot** [00:23:52]
Yep.

**Chenyu** [00:23:53]
Great.
OK.
That's all I have.
I will be in San Diego this weekend.

**Geohot** [00:24:06]
Cool.
Yeah.
I'll be there too.
See you there.

**Chenyu** [00:24:13]
Cool.
next is driver and very nice a lot of nice hcq cleanups Nimlgen

**Nimlgen** [00:24:19]
yeah so yeah I think some still something else to do in hcq so we'll do this week and for AM so
Actually, I've been debugging, like, the access out of the GPU to system memory.
It doesn't work right now.
I mean, I don't know.
Actually, I don't know why, because we have IOMMU disabled, so everything should be pretty simple, I think.
But yeah, I think, like, one GPU, it has no faults on the GPU, but it just writes nothing to other GPU, to system memory, so yeah.
I'll debug this, I'll..
I'll bring HDMA this week as well.

**Geohot** [00:25:17]
So if you want to hit system memory from a GPU, you have to add entries to that GPU's MMU.

**Nimlgen** [00:25:22]
Yeah, yeah.

**Geohot** [00:25:24]
And you're doing that.
It's still not working?

**Nimlgen** [00:25:30]
Yeah, yeah.
Yeah, I mean, it's just basically..
Yeah, there is a special flag called system memory on the page table entries.

**Geohot** [00:25:41]
Yeah, that's what it was on the video.

**Nimlgen** [00:25:44]
Yeah, yeah.
And you just set in the memory controller address.
And this way, you can access other GPU system memory.
Yeah, that's basically what they do in their driver.
I just checked all the physical addresses.
They match what they map in the PTs.
So yeah, I think something's missing.
We'll find this.

**Geohot** [00:26:10]
Yeah, we've got to make sure we can go fast to the other GPUs also.

**Nimlgen** [00:26:16]
Yeah, I think they just also use large bar for this, like for P2P.

**Geohot** [00:26:24]
These large what?

**Nimlgen** [00:26:27]
Large bars, I mean, they just, yeah.

**Geohot** [00:26:30]
Oh, yeah, yeah, yeah.
Our driver does not have to work at all on small bar systems.
I'm never dealing with that.
Yeah, you have the whole chunk on the PCI bus.
How did the VFIO stuff work for the interrupts?

**Nimlgen** [00:26:57]
I got interrupt controller, like the hardware setup on the GPU, but I haven't hooked up with VFIO yet.
So, but basically, yeah, it should work.
I mean, there is quite annoying because you have to like load VFIO with no IOMMU flag on such systems.
But yeah, apart from that, everything works.
So yeah, but it's not final yet.

**Geohot** [00:27:08]
Wait, so VFIO can work with the IOMMU?

**Nimlgen** [00:27:25]
Yeah.

**Geohot** [00:27:27]
I mean, it'd be interesting if this stuff worked with the IORMU, too, if that's easy.
I don't know if it's just like a question of like, there's some API for Linux saying, like, expose these device renders to each other or something.

**Nimlgen** [00:27:51]
So yeah, I mean, like, API looks pretty easy for this.

**Geohot** [00:27:58]
I mean, yeah, we can also turn it off, too.
But this is the driver that we're going to run on our cloud machines.

**Nimlgen** [00:28:04]
But I think on our systems, they have it off.

**Geohot** [00:28:09]
Yeah.

**Nimlgen** [00:28:10]
Yeah.

**Geohot** [00:28:13]
Yeah, we're going to have a cloud probably in about two weeks.
So we're going to have nine of these machines, so hopefully the driver's ready by then.
A few key things that I want to work really well in the driver, too, are fast copying over Ethernet and fast copying over drives.
I want to be able to get 20 gigabytes a second from the RAID array, even the RAID array on a remote computer, because it's going to be super important that our API is capable of loading models in quickly.

**Nimlgen** [00:28:50]
Mm-hmm.

**Geohot** [00:28:52]
You're going to throw the whole hash of Llama7b into the thing.
And this is why things like the tar thing are so important.
Because then you can just run them on remote tensors.
Like you'll run ggufload or tarload on the remote tensor that's on the remote drive.
But it won't be on the remote drive.
It's just going to load the entire file into the GPU's RAM and then chunk it up appropriately.
But yeah, it's that 20 gigabyte load that I want to be one second.

**Nimlgen** [00:29:27]
So I mean, interesting if we can use the DMA memory and just do peer-to-peer to NVMe.
Because currently, we do this IOE ring, and it still goes through this system memory.

**Geohot** [00:29:45]
Yeah.
It should be fast enough to go through system memory.
I'm not that worried if we have to go through system memory.
But, yeah, I mean, if it's easy to go right to the drive, let's go right to the drive.
But I see, like, the system should have 200 gigabytes per second of memory bandwidth.
So, like, 20 should be nothing, especially for dealing with the remote ones, too.
The files are not going to be always located on your machine.
That file that you're trying to read may be located on one of the other cloud machines.

**Nimlgen** [00:30:26]
Mm hmm.
So yeah, I think, yeah.

**Geohot** [00:30:31]
I mean, that could be DMA too, if we could get DMA to work through the network card.

**Nimlgen** [00:30:37]
Yeah.

**Geohot** [00:30:38]
Have you looked at all, by the way?
Oh, go ahead.

**Nimlgen** [00:30:41]
Yeah.
No, no, continue.

**Geohot** [00:30:46]
Do you have a preference for Ethernet or InfiniBand?

**Nimlgen** [00:30:51]
I think, no, not really.

**Geohot** [00:30:54]
Cool.
No, I think, yeah.

**Nimlgen** [00:30:57]
We can support either API.

**Geohot** [00:31:00]
Great.
Well, we bought both switches.
The cards support both.
So we'll be able to experiment with both.
But yeah, no, I'm really excited.
This is all coming together.
Big graph, AM driver, some real management around speed, new gradient API.
the clouds coming together, the clients coming together.
Exciting times.

**Chenyu** [00:31:34]
Great.
So before we move to bounties, for people in this chat, for people in this meeting, if you have any questions about Tinygrad or TinyCorp, feel free to post in the chat.
You can post in general or post in the chat that's attached to this VC.
Speaking of which, what were the status for Comma to adopt Tinygrad now is it still too slow is it on us?

**Geohot** [00:32:09]
um comma reverted it yeah i think it's still too slow so well i got them another millisecond and a half uh with block um but then there's a bug uh which is not something i don't really want to fix till we have big graph but um
If you, there's copies, it takes five milliseconds to do these stupid copies from NumPy because it's all scheduling, but you should be able to put the copies into the JIT.
But for some reason, when you put the copies into the JIT, the test fails.
So I have a failing test for it, but I don't really want to, it touches all the same stuff big graph touches, so.
It's delayed on big graph before we can get them.
Speed that will actually outperform the old.
With the block change, and if we fix these copies, it will actually out perform the old Tinygrad, finally.

**Chenyu** [00:33:00]
Yeah, I think what we'll have, we'll probably do a release after we delete lazy and fix all the things around it.
So maybe then that would be a good time.

**Geohot** [00:32:11]
0.11.0!

**Chenyu** [00:33:14]
0.11.0? That fast?

**Geohot** [00:33:17]
Yeah, I think so.
Yeah, we delete lazy.
That's like the biggest thing that's happened in like a year.

**Chenyu** [00:33:22]
Yeah, no, I mean, it's not like those minor numbers have big meanings, but sure.
We are we are passing a comma release number very soon.
In the very.
We're going to work.
That's the current status of Fuse arange.
I think this is all built on top of Big Graph.
So Fuse arange, Fuse Conv backwards, a lot of these kernel fusion or split kernel would be happening after Big Graph.

**Geohot** [00:34:07]
Yeah, Big Graph is going to be where all this performance really starts to show up.
Once we can do rewrite rules for that, a whole new world.

**Chenyu** [00:34:20]
Was the better cache utilization for comma thanks to block intentional or coded, or was it a side effect of being less stupid?
I think this one, for a specific reason, it's being less stupid.
Block is a better abstraction.
For now, the order is kind of a heuristic, but you can imagine for the
Block order itself is something that can be searched later for potentially faster.

**Geohot** [00:34:53]
It's not just block order.
It was even dumber than that.
It actually was a side effect of being less stupid.
What was happening is you had like, just think of how bias works, right?
First you do the convolution, then you load the biases, then you add the biases, then you store.
But it was doing this in this other order.
It was doing the load the biases, the convolution, the add, then the store.
But the load the biases, the add, and the store are all part of the same block.
There's no reason to ever separate them.
There's zero advantages ever to separating them.
So yeah, that was the side effect of being less stupid.

**Chenyu** [00:35:38]
Better heuristic.

**Geohot** [00:35:41]
Sure.
OK, maybe someday.
Maybe someday you want to separate.
They're both correct, I guess.

**Chenyu** [00:35:48]
Yeah.
No, I think it's faster.
So that's great.
OK, we'll go back to active bounties.
Tensor cores.

**Ignaciosica** [00:35:56]
Hi, hello.
Last week I fixed the swizzle in the TensorCores, so now it's merging views the correct way.
And I've been working on..

**Geohot** [00:36:11]
Did you get that merged?

**Ignaciosica** [00:36:16]
Yes.

**Geohot** [00:36:19]
Oh, I missed it.
Cool.

**Ignaciosica** [00:36:20]
I think this is still a minor cleanup pending in rewriting
the fixed ShapeTracker function.
I think that was the feedback from Qazalin.
But I think that it comes after what I was going to say now, that I think that for complex thread patterns from the WGMMA, we are going to need to swizzle the output.
And I'm working on that, on a clean swizzle of the output.

**Geohot** [00:37:06]
Yeah, swizzling the output's totally fine.
OK.
But yeah, no, that's really good.
You got the swizzle to be used the right way, right?
Not like the fake swizzles were before.

**Ignaciosica** [00:37:19]
Yes.
It ended up being a small, minor change, but pretty fundamental to how
The views add together.

**Qazalin** [00:37:30]
It's like one line.
But if it's one line, then it's like.
It was actually pretty similar to the stuff I did last week with the views.
Perfectly matching lazy.
This all ended up just being one concept.

**Geohot** [00:37:46]
Which PR was it?
Oh, you did.
Oh it was swizzle load ST.
What was the number?
7991.

**Qazalin** [00:37:58]
7991.

**Ignaciosica** [00:37:58]
No, 7951.

**Geohot** [00:37:59]
[7951](https://github.com/tinygrad/tinygrad/pull/7951), okay.

**Geohot** [00:37:59]
Ah, TrueTC Swizzle.
Wow, I missed this.
Cool, great work.
I think I owe you a bounty for that, right?
Yeah, $400.
Cool.
Yeah.
Email me.
I can pay you via PayPal or ETH.
I can't believe I missed it.

**Ignaciosica** [00:38:41]
No, thank you.
And one minor thing is the thing I believe that the patterns you had to try an error.

**network issues..**

**Chenyu** [00:40:00]
So tar extract, you already said why it is important.
I think it's almost done.

**Geohot** [00:40:03]
Yeah, I think it's almost done.
No, I really like it.
Just using, yeah, basically implementing stuff for a tensor file.
Yeah, I think it's good.
Oh, yeah, we need it for, we're going to need it because you're never going to actually have these things as files on your system.
Once this is cloud equals one, you're going to have a cloud tensor, and you're going to want to run tar extract on the cloud tensor, basically.

**Chenyu** [00:40:32]
Do we have lines to merge that?

**Geohot** [00:40:35]
No, we don't.
Gotta wait for big graph.
So yeah, look, I already got plans to waste the lines.
I'll find the lines for this tomorrow, too.
Yeah, I think that can go in tomorrow.
That's good.

**Chenyu** [00:41:08]
I can speak for ONNX.
I think there's a merge of few methods.
few more tensor functions I think there's one for pad and one for selu that those I will review later after the meeting and should be pretty much done after this
I can talk about QwQ as well.
I was just curious what that is, because people are making hype on twitter.
So Flata is doing that.
I tested locally, and I just have some small nits to the PR.
So that should be merged and finished.
Unless, Flata, you have something else to add for that?
Or you can talk about what other things you're interested in working on.
I know you were training RetinaNet and stuff.
How's that going?

**Flata** [00:42:18]
Just doing the losses, because I was trying to figure out the masking.
But I talked to geohotstan on that.
So should be moving along.
But hopefully, I can put up a PR pretty soon.

**Geohot** [00:42:31]
Not sure how soon, but hopefully soon.

**Chenyu** [00:42:38]
Yeah, some ONNX and ONNX.
I'll split them up.
I will post them this week.
Great.
It's working.
It's progress.
So that's ONNX.
Great.
Do I have anything left from the agenda?

**Geohot** [00:42:54]
I talked a little about the cloud, too.
Yeah, so basically for everyone who's frequently in these meetings, everyone who's developing, everyone basically who's gotten a bunch of.. Everyone who's gotten pull request merch to Tinygrad, you guys will all be in the cloud beta program, which will be free access to the Tinygrad cloud.
Again, it's a trusted thing.
I think they'll probably be like..
30 people here who get access to it.
I'll send you guys all, I'll make a channel.
I'll send you guys all API keys.
Basically like a way to get an API key if you have a Discord role.
And then, yeah, you'll be able to use your very own 7900 XTX in the cloud and use it for whatever you want.
You'll be able to open multiple as well.
So I think within months, I'll try to like set some limits so like each API key can access like 4 GPUs or something.
There'll be no guarantees on the locality of those GPUs to start.
So it'll be a slow path between them.
But yeah, if you want to run four training experiments, I think it'll be super easy.
And yeah, we can grow the cloud from there.
But about a month away.
So we've got to get the computers up.
We've got to get the AM driver finished.
We've got to get big graph merged.
I'm going to write the renderer and the compiler and graph rewrite transformations.
It's like factorial.
It's like you cheat your little graph rewrite, you write a little assembler.
That's how my mind's working these days.

**Chenyu** [00:44:36]
Yeah.
I don't know.
I don't play the game.
It feels too much like working.
But again, I was playing other programming games last night, so I don't know.

**Geohot** [00:44:52]
Oh, you're doing advent of code?
I'm doing advent of code.
We've got like a five-minute time today.
I've got to warm my fingers up.
No, it's nice.
It's 1 o'clock here, so I'm awake at work for it.

**Chenyu** [00:45:13]
Yeah.
We're training ResNet over cloud.

**Geohot** [00:45:15]
Yeah.
Yeah, training ResNet, get LLMs working.
What's up?

**Chenyu** [00:45:31]
Great.
That's everything I have on the agenda.
For people, any questions, comments?
Oh, probably.
I think the MTL compiler's service is good if one slows.
Small things are fixed.

**Geohot** [00:45:52]
Yeah, it's been a long back and forth on those things.
I wish you would just sit down and very carefully read that PR.
I'm looking through the cache directory, and I expected to see things go there.
There's actually just one 0 byte file there.
So I think that's something we still don't understand about that.
But it does actually make Metal, it makes the Metal compilation parallel.
So BEAM for Metal is like twice as fast, which is cool.

**Chenyu** [00:46:24]
Great.

**Geohot** [00:46:31]
Oh, I locked it down.
Did I?

**Chenyu** [00:46:35]
Yeah, it's locked.
Cool.
Yeah.
Is there a BLAKE3 that is locked?

**Geohot** [00:46:50]
Is there a what that's locked?
Oh, a black three.
Yeah, there could be, I think.
Um..
Where's the BLAKE3?
OK.
He's working on making it faster.
I will look this one over.
And I have locked Bounty.
I just didn't lock it in the spreadsheet.
Yeah, we need BLAKE3 for Cloud.
BLAKE3 is going to be the hashing function of Tinygrad.
When you request a tensor, you're going to request the BLAKE3 hash on it.
we can't use something like SHA3 or SHA256 because you can't do them parallel really fast, right?
Who wants to sit there forever while you're computing the SHA hash in a 20g file, right?
I want to basically compute this at, I want to be able to compute that in 50 milliseconds.

**Chenyu** [00:47:37]
Oh, and has been doing some cleanup improvements to div and mod.
Or think about if I can make it a bounty or something for the ultimate goal.

**Geohot** [00:47:55]
Absolutely.
No, I think he's doing great work.
Oh.
I see the fast idiv.
This is like a classic.
I've always wanted this in Tinygrad.
Nice to see it.

**Chenyu** [00:48:16]
Yeah.
HAL abstraction in HCQ device?

**Geohot** [00:48:21]
Yeah.
Yeah, I think if Nimlgen has time for that.
I think it's nicer than hooking the IO controls, because then we have a path for making these things work on Mac.
And just hooking the intercepting the syscalls is kind of sketch.
It's fine for the IO control sniffers, but to do it for, we should write a proper mock framework.
It's a small API to mock.
So yeah.
Nimlgen, did you think you could do that?

**Nimlgen** [00:48:52]
Yeah.
Yeah.

**Geohot** [00:48:56]
Cool.
Does the abstraction I wrote make sense?
Do you see kind of why?

**Nimlgen** [00:49:10]
Mm-hmm.
Yeah.

**Chenyu** [00:49:16]
Float in sim infer?
Oh, I think the author has a question that, do you want global ops and global mem to be float if you also allowed float in that, or you want to round it to integer?

**Geohot** [00:49:31]
Oh, round it to another.
OK.
Wait, so this is the MyPy one?

**Chenyu** [00:49:39]
No, this is the 7456.

**Geohot** [00:49:45]
Oh, that's an old PR.
Oh, yeah, yeah, yeah.
You can totally ground that.
Yeah, that's fine.
OK.
OK.
Don't see any.
Yeah.

**Chenyu** [00:50:05]
Oh, for downgrade, wgpu, I think Wpmed would look into this further.
Oh no, I think we prefer to not pin a version if possible.
So it's good to understand why it's happening on certain versions, because these things are moving forward.
So it's good to know why it's slow.
If you say it's timeout five seconds, then we want to know if it's legit reason.
Then we see if we can modify the threshold if needed.
Pinning version will be the last thing.
It's like MyPy, even though if we pin it, we actively want to catch up to the latest version.

**Wpmed** [00:50:57]
So I tested it today, and it still times out on my device on the latest version.
And just increasing the time out slows it.
So yeah.
I have to look into the library itself, the wgpu lib, why it's happening, what was the change exactly.
Yeah, but it seems like we need an upstream change for it.
So, I mean, it works on your end and it works in CI, but maybe someone else has a Mac like mine or some slower Mac or something, and they can end up with this timeout as well.
So, yeah.

**Chenyu** [00:51:49]
I see.
I mean, I think it's fine to down-pin the version for now.
I think that makes more sense.

**Wpmed** [00:51:56]
Maybe I can solve it in the lib as well.
I already have PR in the wgpu lib, so I added support for timestamp query and stuff.
So maybe I can fix it.

**Chenyu** [00:52:07]
OK.
Oh, that sounds good.
Every time we pin a version, we still actively looking to bump the version to the latest.

**Geohot** [00:52:19]
Yeah, one of the problems with not pinning it is it updates.
It doesn't update every time you update CI.
It'll only update when the Python packages update, which is like only when someone changes setup.py, and then that's kind of annoying.
But I think it's fine if we don't expect there to be API changes.
But if we expect there to be API changes, I don't know.
I think pinning is kind of the right idea.
Oh, Nimlgen, any reason not to merge RDNA2?

**Nimlgen** [00:52:51]
No, I think it should be good.
Double check if there's anything missing for JFX 10.
Maybe it's, yeah.
I just didn't click merge because, I mean, Woze has access to do that, so maybe he still needs to do something.

**Geohot** [00:53:09]
Oh, that's a good point.
Oh, he could just merge it.
Yeah, yeah, yeah.
That's a good point.
I'll merge it.
Okay.

**Chenyu** [00:53:35]
Sounds good.
Okay.
Now we review the PR.
There's really nothing left.

**Geohot** [00:53:41]
We finished early

**Chenyu** [00:53:42]
Great.
Merge.
Great.
OK, I think that's a meeting for this week.
So next week, we will switch to, I will post this in general a day before the meeting, but we switch back to 9.30 AM West Coast time.
And see you next week.

**Geohot** [00:54:26]
Thanks, everyone.
See you in San Diego.

**Chenyu** [00:54:29]
Bye.

**Wpmed** [00:54:30]
See you, guys.
