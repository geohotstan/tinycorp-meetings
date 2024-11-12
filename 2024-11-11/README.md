# 2024-11-11 Meeting

### Audio

[Recording](https://drive.google.com/file/d/1e-u_BMfIa_oLgkUrg40QgxaOONyaEHeR/view?usp=sharing)

### Chapters

- **00:00:00 Introductions and Tiny Box Sales Update**
  Overview of Tiny Box sales, shipping improvements, and agenda.

- **00:02:48 LLVM Rewrite and Optimization Goals**
  Geohot discusses LLVM rewrite, PTX optimization bounty, and block structure improvements.

- **00:05:48 TinyGrad Cloud Model and GPU Rental Pricing**
  Introduction of the TinyGrad cloud model and GPU rental pricing structure.

- **00:10:21 Stride Optimization and Caching Improvements**
  Discussion on stride calculation optimizations and caching strategies.

- **00:12:34 Hand-Coded vs. BEAM Optimization**
  Performance comparison of hand-coded optimizations with BEAM timing.

- **00:16:29 Release Plans and Python 3.10 Update**
  Timeline for the upcoming release, QCOM fixes, and Python 3.10 migration.

- **00:17:48 Big Graph and Lazy.py Replacement**
  Progress on Big Graph and plans to remove Lazy.py for gradient function rewrites.

- **00:24:51 Driver Issues for AMD and QCOM**
  Updates on AMD and QCOM driver challenges, including memory and compute queue handling.

- **00:33:58 WebGPU Development and Cleanup**
  WebGPU support status, dtype handling, and planned code cleanup.

- **00:41:18 Removing ULONG Emulation and NaN Handling**
  Alternatives to ULONG emulation and NaN handling for streamlined WebGPU performance.

- **00:46:17 Tiny Box Hardware Plans and Future GPU Integration**
  Discussion on PCIe5, potential 5090 GPU integration, and power requirements.

- **00:55:20 USB to PCIe for AMD GPUs**
  Exploring USB connections for AMD GPUs in Comma devices and TinyGrad.

- **00:59:11 MLPerf Update and Google’s TPU V6**
  Preview of upcoming MLPerf benchmarks and Google’s latest TPU V6.

- **01:01:11 PCIe5 Feasibility and AMD Driver Support**
  Feasibility of PCIe5, NVMe, and AMD driver support over USB.

- **01:11:28 Cloud Access for Tiny Box Users**
  Demonstration of Tiny Box compatibility with TinyGrad cloud access.

- **01:13:50 TinyGrad Book Idea**
  Brief discussion on publishing TinyGrad source code as a book.

- **01:16:03 TPU Backend Prospects and Final Remarks**
  Consideration of TPU support for TinyGrad, followed by meeting wrap-up.


### Transcript

**Geohot** [00:00:01]
Welcome, welcome people to meeting.
Yeah, I @-ed everyone.
Maybe 1 to 1 for the meeting.
I think there's.
You know, I did a stream today.
So It'll be on Georgehotz archive so there's gonna whole bunch of good tinygrad stuff in the stream.
I, without preparing at all, launched the new cloud stuff on my phone, on my literal Android running Samsung Z Fold 5, and everything just worked.
So that was really cool.
And the new cloud stuff also allows, it hides latency pretty well.
So you're pretty much just making one round trip per step, which is still too much, but at least that's a start.
Then the way around that is gonna be With things like stunning mnist we sold like four tiny boxes this week.
So it's a good week for tiny box sales And it turns out one person got shipped a tiny box and didn't pay for it So, uh, yeah, you better pay for it or I will uh
and my goons and they will come get the money.
We will make sure this never happens again.
You have to pay before we ship the tiny box.
But yeah, we sold like four this week, so that's a good week.
We're building 28 tiny box pros.
We have a couple of pre-orders for those.
If you want a pre-order for a tiny box pro, I think we have like three left.
So it's $2,000.
That's a pre-order for a $40,000 TinyBox Pro, which has everything in it that you need.
If you want to discuss in general stuff, or there is a chat for the Reds only VC, but I kind of like it better in general.
If you guys have anything to discuss, remember that on topic rules apply.
This is a highly on topic discord.
I see created AGI.
Get out of here.
Get out of here.
This is a meeting.
I regret @-ing everyone.
Okay.
So I guess the first ones are for me.
I rewrote LLVM in a much more modern style.
So if you want to read that, it's llvmir.py.
It's just a bunch of pattern match rules, very short amount of logic, maybe 40 lines of logic.
and the rest are just pretty much string creating pattern matcher rules.
So, yeah.
And then if someone wants to earn $200, you pretty much just have to do exactly what I did for LLVM, but apply that to PTX.
So, yeah.

**Chenyu** [00:03:01]
Is the new LLVM faster or slower or similar?

**Geohot** [00:03:07]
The new LLVM is similar, and I spent some time looking into LLVM speed.
I wrote all the stuff to do float4 for folding in LLVM.
It was very fast, but it's not faster, which brought me to the next thing, which is blocks.
So there's a whole bunch of places where we are just picking basic blocks in a stupid way.
For example, sometimes there's loads inside of loops happening multiple times when stuff could just be kept in a register or pushed on the stack.
So that's my block rewrite, which is going to pre-break the graph up into basic blocks before doing layout.
It's actually also twice as fast, which is great.
It almost works.
I have to write something that joins blocks.
Right now, every block only has a single child.
There's no way to express diamond-like things.
So I'll have to write something to join blocks, but that didn't seem fun for stream today.
So on stream today, I updated cloud.
You can try this right now, CLOUD=1.
Cloud equals one separates the tinygrad front end from the tinygrad back end.
And it really points the way to what our future business model is going to be.
We are going to rent GPUs by the second in pretty much any quantity you want.
If you want to, right now, if you're on one machine and you're doing an experiment and you want to do a hyperparameter sweep or you want to try 10 things quickly, great.
10 GPUs.
Start 10 instances of the program.
It'll just connect you to 10 different GPUs.
So yeah, I mean, I think that a lot of the ML cloud stuff, it's either at one of two abstraction levels.
It's either at an abstraction level like AWS or Azure, we are renting a machine, or it's at an abstraction level like openAI, where you're paying for API calls to a model.
I think neither of these are ideal.
The problem with the API calls to the model is it's not portable.
You're getting locked into that.
You can't run different models.
You can't run models differently.
You're opaque to what the sampler is.
They can rug you and update.
Oh, you thought that was GPT-4.
You're getting psych.
It's GPT-3.
You didn't know.
So, you know, you want to avoid all that.
Then the problem with the Azure AWS stuff is, okay, I got to see another machine, put an SSH key in, install this Docker container.
Everything just takes a long time, your environment's not really portable.
So if you have an API key set on your computer, you'll be able to seamlessly train from your MacBook, like you have a big GPU.
from be that a 4090 or whatever.
And then also, one of our value ads as a company is going to be to have done all the beam searches on the back end for you.
So if we develop algorithms to run things faster, it's just like our cloud is very, very fast, and there's this nice orchestration layer.
So yeah, that's cloud.
That's LLVM, and that's block.
Chenyu?
Oh, pricing model, 50 cents an hour.
50 cents an hour for GPU builds at the second.

**Chenyu** [00:06:39]
Do users specify the GPU they use?

**Geohot** [00:06:41]
I don't know.
Uh, that I'm not sure about yet, but it'll be, you know, order of magnitude 50 cents an hour.
Um, and you'll be able to just, I mean, if you want to figure out how fast it's going to go connect to the session, run one step, see how long one steps out and then multiply.
Uh, so, you know, you might not, you might be opaque to the GPU.
and we have to change the API a little bit to abstract that.
Because eventually what we want to do as a company is replace those GPUs with tiny chips completely seamlessly.
So we'll make it both faster and cheaper and better without you having to change a single line of your code.
In fact, without you even being aware because our abstractions are perfect.
You know, there's so many abstractions are leaky.
And I think that our abstraction is not only not leaky, it's also very complete.
So, you know, it's easy to make an abstraction that's not leaky, but let's say you have an abstraction where you're adding one to a number.
What if you want to add two to the number?
I don't know, it only supports adding one, right?
So that abstract doesn't leak, but it's not that useful.
I think we can build both a useful and non-leaky abstraction to describe all of machine learning, basically with, yeah, and then you'll connect to the cloud and you won't care if you're connected to an AMD GPU, an NVIDIA GPU, a TinyCorp GPU, a TensTorrent accelerator, it's all completely hidden from you, which is what you want.
What machine learning practitioner wants to think about what GPU they're running on?
Nobody.

**Chenyu** [00:08:29]
How about any of the CPU component if I'm doing RL.

**Geohot** [00:08:37]
Um, well, what do you need the CPU for?

**Chenyu** [00:08:43]
Maybe simulate based on some environment?

**Geohot** [00:08:47]
Yeah.
Yeah.
That stuff is, uh,
I mean, the problem is you're going across the internet for that.
So that's gonna be around, yeah, that's gonna be around trip time for every action.
Yeah, that's later.
Clouds will definitely be able to do, yeah, yeah, yeah.
I mean, our first, I think our first kind of offering will be LLMs.
Making sure LLMS can run fast, making sure diffusion can run fast, all the things where you don't care about running any part on your computer.
For diffusion, you'll literally just send a tensor with the text and you'll get back a picture, which is the exact API you want for diffusion.
My point is we can clone OpenAI's API, but at a much better level of abstraction.
And it's not like you're going to have to upload the stable diffusion model every time.
You'll just put a hash event and tinygrad automatically take care of that.
So yeah.

**Chenyu** [00:10:01]
That's good.
Oh, what did I do?
Oh, update.
Update to real stride to make it stride better.
I saw your comment saying that something got 50% slower.
How was that?

**Geohot** [00:10:21]
opt.
So when you run external benchmark schedule, opt is where we're applying all the shape trackers and all the optimization shape trackers.
Now all those reshapes and permutes are very slow.

**Chenyu** [00:10:40]
Oh, but I run the script, I reply to your comments.
I think it might be some other comments.
It might be some other PR
but I agree like this as it just makes the shape checker message slower because now we are doing rewrites in these methods.

**Geohot** [00:11:01]
Yeah.

**Chenyu** [00:11:04]
I think the solution might be we kind of want to do this earlier more upstream because now we are doing the same thing in a real stride.
And we also later do the same thing multiple times in the load.
And because we only get the load pattern from Shape Checker, if we only do this once or we cache it somehow, it maybe has time to opt, but it should make later time faster.

**Geohot** [00:11:38]
Yeah, we could.
Is it being cached right now or not?

**Chenyu** [00:11:44]
At what level?
It's probably not cache at all.

**Geohot** [00:11:47]
Well, we could cache the Uops for the shape tracker.

**Chenyu** [00:11:49]
No.
I mean, cache at what function?

**Geohot** [00:12:02]
Like the shape tracker to Uops function.

**Chenyu** [00:12:06]
Oh, yeah.
So that's why I mean, if we move less simplification to let to a to Uop,
a method that maybe everything would be faster in there.

**Geohot** [00:12:18]
Yeah.
If we even just make a two index you opt cache property on the shape tracker, that might be fine.
We could try that.

**Chenyu** [00:12:34]
So I was looking into the hand-co-optimization.
There are like closed layer that has no test.
I have no idea what it's doing, but
I have a script that computes a hand-co-optimization versus BEAM=2.
Then I realize hand-co-optimization, if you just measure it per kernel level, it's not too bad.
Our aggregate is pretty bad.
Thinking about how to do that better.
I want a sequence model that I can just apply methods to things without really compiling anything.
Then that would be the new hand-co-optimization.

**Geohot** [00:13:13]
But how could hand-coded optimization not be that bad individually?
It's terrible on a whole bunch of things.

**Chenyu** [00:13:20]
Oh, how do you define terrible?
Even wins like 20% of the time.

**Geohot** [00:13:23]
Over beam?

**Chenyu** [00:13:27]
Yeah.
Oh, I mean, granted, loads are maybe small kernels.
And it might as well.
So that's why I started looking into the beam timing thing, because I was maybe that's why.
But indeed, there's a difference in that.
When I started to test BEAM, then I realized BEAM on metal, on both M1 Max and I got a new M4 Max are both slower than Torch MPS.
That was my last point that I was going to investigate this week.
Either BEAM just lowers on power.
Yeah, so BEAM is slower somehow.
I saw your picture on LLVM, but it's also slower on MPS.
And I don't know if it's a BEAM that has a bug, because you know, we not mask a lot of compile errors.
So maybe the scope issue bug is that big that we mask a lot of good kernels.
Oh, I wasn't.

**Geohot** [00:14:29]
Yeah, I'm definitely worried about that mask.

**Chenyu** [00:14:33]
Yeah, that was my plan for this week.
Wrong, like strict BEAM on these and see what's happening with BEAM.
BEAM is also slower for ResNet.
Only a few percent, but slower, so.

**Geohot** [00:14:48]
I mean, Torch MPS got faster.

**Chenyu** [00:14:51]
Yeah, Torch MPS is pretty fast.
I also don't know why, but for our benchmark on M4 Max, some of it slower than my M1 Max.

**Geohot** [00:15:05]
It seems like a bug.
We might be masking compiler or is there something?

**Chenyu** [00:15:11]
Yeah.
We are definitely masking compiler.
And oh, so you saw my fix, tweek your fix because now Metal Compile does nothing and the compilation is in runtime.

**Geohot** [00:15:25]
Yes.

**Chenyu** [00:15:26]
So because I hit let during BEAM, so we are definitely masking something.
That might be faster.

**Geohot** [00:15:38]
Yeah.
Um, you understand why I moved that.
I'm sick of the conda people complaining.
That's like one of the biggest like first, first issues with tiny grad.

**Chenyu** [00:15:50]
Yeah.
Yeah.
That I understand.

**Geohot** [00:15:56]
Which reminds me, we have to do a release.
We haven't done a release in a long time.

**Chenyu** [00:15:60]
Uh, yes.
Now we can do a release now.
Now a good time.
Oh, no, we kind of want to fix QCOM.
We kind of want to fix the QCOM.
Because we can do a release.
No, we were saying we want this release to be the version that commaai can apply to.

**Chenyu** [00:16:29]
Oh, can use?
But also, any objection to Python 3.10?

**Geohot** [00:16:40]
no longer supporting 3.8.
Okay, that's merged.
And new cloud cost us 30 lines.
Sorry about the 30 lines.

**Chenyu** [00:16:53]
Where are we now?
9950 something?

**Geohot** [00:16:56]
9940.
I saved lines with LLVM.
our new cloud is a ton more usable over the internet.
We're at 9930 now.

**Chenyu** [00:17:14]
We can probably clean something up.
Now we are at 310.
You're right, some pattern manager.
We don't have all the if else.

**Geohot** [00:17:24]
Yeah, I like the match case syntax, even if it's not faster.
It's just so much easier to read than a bunch of instances.

**Chenyu** [00:17:28]
Sounds good.
next for qazalin.

**Qazalin** [00:17:48]
So, um, I'll post the issue for big graph in the chat as well.
Uh, I am working on milestone four, which is I think the hardest of all of them.
So basically we need to, uh, find a perfect pattern matcher syntax for the swizzling and the grouping.
Because what I've realized is that the swizzling is actually very incomplete and lacks a lot of stuff because the way I built it was mostly for single reducing and stuff like that.
But I'm pretty excited about this.
So this is like the last blocker to removing lazy.py completely.
So far, big graph is being created
the initial realizes are with new paths.
Now all that's left is all the sophisticated grouping logic, like group a reduce op with his children.
So, or group a double reduce stuff like that.
So I'm thinking about how to do more.

**Geohot** [00:19:02]
Even if some of the stuff isn't in,
isn't in pattern matchers yet.
How soon can we delete lazy.py?

**Qazalin** [00:19:12]
Do you think deleting lazy.py is more important than moving all of this to pattern matchers then?

**Geohot** [00:19:26]
Yeah, because until we delete lazy.py, I can't rewrite the gradient thing.
where I want to change the backwards API to no longer have dot backwards and requires grad.
I want it to be like a lost dot gradient list of tensors.
But until we have Uops, I can't do that.
So I do think, yeah, deleting lazy.py is the highest priority, higher than making everything a pattern matcher.

**Qazalin** [00:20:00]
I will reprioritize then.
Yeah.
I think it's possible to do it beforehand.

**Geohot** [00:20:08]
Cool.
Yeah, I mean, if it's extra work, we shouldn't do it.
But if it's just kind of a choice for which one to do.
Yeah, I think the UOP thing is higher priority.
That also gets us a lot of lines.

**Qazalin** [00:20:22]
Sure.
Yeah.
I think that has other challenges like
How do you deal with buffers and stuff like that?
But I think tinygrad has some base work for it that we can translate to tinygrad.
Yeah.

**Geohot** [00:20:35]
So I think the way you want to do buffers is just make a global dictionary that maps Uops, a weak key dictionary that maps Uops to buffers.
I think that's all you need for that.
And then I think you can support even the same method that's on lazy.py.
I have all that toonygrad stuff, which can all the methods that are on there and stuff.
All those to shape and device methods and stuff.

**Qazalin** [00:21:12]
So yeah, I'm starting to add the movement ops to UOP, which is pretty interesting.
At this point, I say it's possible because lazy buffer is basically like a graph container, at least how the scheduler view does to print down.
And it's going to be very easy to, I think, very easy to move all of those to UOP.
Rewriting all of those patterns to UPAT is harder, but I'll figure that.
I think we're getting to a point where it's like, you have this very large graph of a bunch of swizzles and you push through whatever you can.
The moments it can't be pushed through, you just make that the store and realize that that's like the big idea.

**Geohot** [00:22:04]
I don't mean to interrupt your process.
If you think you're making good progress here, then by all means keep it this.
But I'd be really happy if by the end of by next Monday, we could have lazy.py gone and then I could rewrite the gradient function.
The problem with rewriting the gradient function now is when buffers are realized, their parents are deleted.
The parents are deleted, a lazy buffer.
And then there's no way to compute the gradient if you don't have the parents anymore.
But in UOP, it stays around forever.
I mean, that's a whole nother challenge.

**Qazalin** [00:22:12]
Oh, you want to keep the scoreshift?

**Geohot** [00:22:16]
Well, nothing is going to be deleted on UOP.
UOP is immutable.
but you don't keep the UOP around.
Only as long as the tensor's around.
Once the tensor goes away, the UOP goes away.
But if it's still apparent, it'll still be around.
But I think that you will delete the UOP from tensor once it's realized, and then it'll just be the buffer.
So there's a slight distinction here where it's like, if you realize the tensor, the UOP will still exist if there's an unrealized child that goes through that tensor, but the tensor itself no longer has a pointer to the UOP.
I don't know.
Maybe we should split this up.
Maybe you keep working on this and I'll take a look at the lazy deletion.

**Qazalin** [00:24:01]
I think what I can do is I can move everything in the schedule there to you up so that you're not blocked out by the schedule.

**Geohot** [00:24:11]
That sounds good.
If that's doable, that'd be great.
Yeah, the earlier you can do that, that movement, the better.
And then I can do that after I finish block.
Cool.
All right, AM drivers and QCOM issues.
I see that we launched a kernel.

**Nimlgen** [00:24:51]
Yeah, so.
AM works.
We can run some models and it's just correct.
I just tested GPT2 and it's fine.
So the next step is just to clean up and rewrite all these page tables and virtual memory stuff.
I think I'm just going the
Like the old way, like we will just map pages in like this backend style and not in TinyGrad and with memory planning.
And maybe after that, we can think like how many, so if we need all these virtual memory, we can just access memories in like.

**Geohot** [00:25:38]
Yeah, I think it's a good idea to support it.
I mean, it'd be hard to do with it.

**Nimlgen** [00:25:45]
Um, yeah, so also, yeah, it works.
I mean, um, we need, I think, but speed is a bit way slower right now.
Yeah.
I need to check all this power management, uh, they do in the driver.
So currently this is missing.
So yeah.
And I think we just simply runs with the boot clocks for now.
So it's slow.

**Geohot** [00:26:13]
I have a theory that it's going to be way faster once you get that.
I think the driver is messing up.
I don't understand how the AMD one computes the first four matrix multiplies slow and then speeds up.
The driver's got all sorts of issues there.

**Nimlgen** [00:26:32]
Yeah, I've seen that behavior, yeah.
Yeah, also we don't use mess, so we just use only one.
keek queue, which is not actually a mess, but it's called, yeah, mess keek.
So we just ask Carol C to just start this queue as a scheduler, but it just done only just to map our compute queue to the Mac.
So yeah, we don't use mess.

**Geohot** [00:27:07]
So wait, wait, wait.
You're using the mess queue or the MEC queue?

**Nimlgen** [00:27:13]
No, I mean, we, so no, we have two queues.
So we have the compute queue, which is run on MEC. So it just, just the compute queue.
So actually we can ring any doorbell.
I mean, it just set up in the MQD. So,
No, no, I mean.
We don't use mess, which is completely skip this.

**Geohot** [00:27:48]
There is only do we even have to load the do we even have to load the IP block?

**Nimlgen** [00:27:57]
So actually there are two IP blocks for mass.
One is just the actual mass which is like the scheduler and you can send all these messages like schedule or just save or just do this compute wave restoring and they also have like mass kick which is kernel interface queue and that's
Like before mass, it was just a key queue.
Now they moved it to mass-kick.
I don't know why.
But actually, that's the first queue that should be set up.
And it does nothing.
So it's different from where for them.
So I think it's not the mass, it's just the old key queue, which runs a bit different pockets.
But yeah, so we just use this queue to map our compute queue.

**Geohot** [00:28:52]
I see the, uh, uh, Felix from AMD mentioned using this, but using it through the driver.
I don't know where that he posts on like an issue or something.
I post on a gist.
Yeah.
He posted, he posted, uh,

**Nimlgen** [00:29:24]
So yeah, because in the original driver, they use this key queue to map mass.
And we just don't don't map mass, we just map compute queue.
Got it.
So yeah, we just skip it.
Yeah.
So for QCOM, I'm just looking into this.
It's just, you know, registers looks correct.
I think we just got a pretty big kernel, which has 25 textures and I
And I think Q-com, I mean, GPU OpenCL Q-com also executes all them with one kernel, but it's... I don't know, I think... I don't know where it puts all the last nine textures.
Because, like, the buffer it uploads, it just contains only 16 textures.
At least the size, like, they use just only for 16 textures.
So I think that's what Misen and I investigated.

**Geohot** [00:30:27]
Got it.
I mean, whenever we have limits like that, we have to add asserts.
Right?
Like, I don't, I never wanted silently dropping non-buffers.

**Nimlgen** [00:30:35]
Yeah, sure.
I mean, I don't know, generally, I know, hardware can just
use more than 16 textures.
I don't know why they just split into several buffers when they upload them or something like that.
So, yes.

**Geohot** [00:30:53]
But you know, either way, the thing I never want is for it to silently get the wrong answer, I would much rather at a certain time to get the wrong answer.
We also added, Harold put up a pull request to merge in the NumPy stuff.
And why is that so slow?
Why is it taking five milliseconds to copy a kilobyte?

**Nimlgen** [00:31:17]
Yeah, we... Like the raw Carpus right now is a bit slower on QCOM compared to the OpenCL.
Like, OpenCL Carpus at seven gigs a second and we do five gigs a second.
And that's because the caching, I mean, we use, I think, the wrong caching scheme.

**Geohot** [00:31:41]
And yeah, I mean, I live milliseconds, though.
Five milliseconds at five gigs a second is 25 megabytes.
And these buffers, I think, are only a couple kilobytes.

**Nimlgen** [00:32:12]
Yeah, OK, I'll take a look into this.

**Geohot** [00:32:17]
It's on stats.tinygrad.org now.
That was what was responsible for the big spike around the 5,200.

**Nimlgen** [00:32:33]
Yeah, because I think I just only tested on the biggest sizes than this.
Maybe we have some latency or something.

**Geohot** [00:32:46]
Cool, yeah, great work getting a kernel to run.
And then we're polling, right?

**Nimlgen** [00:32:58]
Oh, yeah.
I mean, oh, yeah.
Also about the interrupts,
Yeah, we're just polling.
Actually, I think we need to interrupts for two reasons.
And I think the page files, but I think this is the least important because we can just wait for time out, I think.
Or we can poll the registers and see if something went wrong.
So that's fine, but they also have
Thermal alert which is also they use as interrupt.
Well, so I think we Ideally we also want these I think so do not kill our GPU

**Geohot** [00:33:58]
Yeah, yeah, yeah, these things are I mean
We might want to check the temperature if it's thermal.
But yeah, no, I doubt this is going to.
Again, it's AMD.
So you can't take anything for granted, but at least with the Qualcomm chip.
The Qualcomm chip has a hard power off at 110.
So I think the worst case, if we ignore that, is that the GPU will just hard fall off the bus.
Is there any way that, oh, I mean, interrupts would be great just so we could not, we could not have to spin the CPU if there's any way to do it without a driver.

**Nimlgen** [00:34:45]
Yeah.
No, the only way I just found is like to map this in kernel.
I don't know if we can set up RQ from the user space.

**Geohot** [00:34:54]
I'll investigate this better, but yeah.
And then which file is it right now?
I mean, I see some stuff in ops AM, but this is not like setting up all the firmware stuff and stuff.

**Nimlgen** [00:35:09]
Yeah, yeah, it's I'm just going to move this into the kernel.
But the actual, it's just an extra, just extra AMD PCI and all files there.
Like PCIE two and all the IP blocks there.

**Geohot** [00:35:28]
PCIE two was the main one I could run and actually do this.

**Nimlgen** [00:35:34]
Yeah, Op_am also works, which is the expertise.

**Geohot** [00:35:39]
Wow, this is a lot of code.
I wonder how much we actually need.

**Nimlgen** [00:35:41]
Yeah, I think not.
Yeah, definitely, I think we can rewrite a lot and it more clean away.
So yeah, I think it should be a lot cleaner.

**Geohot** [00:35:57]
Awesome.
Cool.
Lets move on bounties
WebGPU, where we at on this?

**Wpmed** [00:36:23]
I think we're close.
I did support for new Dtypes and I'm working on stable diffusion export to make it work again.
Once I have stable diffusion exported, I push it, need a little more cleanup.
And then I think this week, it's probably can be mergeable, well, depending on lines, of course.

**Geohot** [00:36:48]
But yeah.
We'll get you lines, even if it means deleting PTX.
OK.
Cool.
The style looks pretty simple.
I see you've moved away a lot from these style of stuff.

**Wmped** [00:37:17]
Yeah.
So a lot of better mature stuff you see is this bool stuff, bool hacks and...
You carry short acts, things like that.
Yeah, I check if I can, I can merge more with C-style.
So I feel like there are some lines that you still can be cut off.
Yeah, so I take a look if I can, I can merge stuff with C-style.
It's because WSGL is not C-style technically.
Even when you cast, it's more like a constructor expression when you cast.
In C-style languages, you cast with parentheses and then you have the type button.
In WSGL, you have the type and then it looks like a function called a constructor expression and there's a lot of other weirdness.
which makes it not C-style, but this is just like the language itself.
But still, I think there might be ways to merge more of this stuff with C-style.
So, yeah.

**Geohot** [00:38:31]
I also still want to get rid of the ULONG stuff.
I want to switch three fry itself to just use ints and not use ULONGs and then not do this emulation.

**Wmped** [00:38:43]
Yeah, I also wanted to do that.
I have a look.
I already tried it once, but I give it another try.
So my thinking was to somehow vectorize.
So instead of using ULong, we could vectorize the int and then just work with that.
So I want to avoid the ULong buffer completely and I couldn't get it to work yet, but yeah, I will.
I will take another look.

**Geohot** [00:39:12]
I can look into that.
I can look into the three fry thing.
Yeah, no.
I mean, before we converge this, there's way too many of these string rewrite rules here.
Like I don't understand why the normal infinity rewrite rules from C style don't work.

**Wmped** [00:39:29]
Because infinity is a weird new webGPU spec.
So there's a lot of bug there that I have to work around.
If you look at it, there is a special isnan because in any other languages you do A not because A and this basically means you want to know if it's nan, but that doesn't work.
in WebGPU.
So I found this workaround.
And so about infs and names, they're just workarounds because how WebGPU is.
And so I can't change the spec and how these runtimes work.
So what I can do is add rewrite rules to workaround.
But I also hate this.
I also hate this as much as you do.
But I wish I could do more.
Yeah.

**Geohot** [00:40:20]
No, no, no, but I'm reading the specifically the infinity rewrite rules.

**Wmped** [00:40:24]
Yeah.

**Geohot** [00:40:24]
They look identical to me to the ones in C style.

**Wmped** [00:40:30]
Okay, let me see.
Right.
You mean the cards?
Which line?

**Geohot** [00:40:36]
75 and 76 in your pull request.

**Wmped** [00:40:42]
Oh, yes.

**Geohot** [00:40:43]
Identical to the ones in C style.
except that maybe your render D-type thing.

**Wmped** [00:40:51]
Yeah.
Exactly.
The render D-type.
Yeah.
Because you see in C-style, you have the parentheses inside that you have the D-type, but in WSGL, you have just the D-type and then the parentheses because of different casting syntax.
But yeah, there might be.
Yeah.
It might be mergeable.

**Geohot** [00:41:18]
A lot of this char and short stuff, things are generally better to be PM rewrites than to be string rewrites.

**Wmped** [00:41:33]
Yeah, I know which ones are you talking about.
I can move those too.

**Geohot** [00:41:38]
These hacks for nan is going to make everything so slow.
You can't, this doesn't work.
You can't, you're rewriting all multiplies to have a where?

**Wmped** [00:41:51]
No, not all, not all, just, just where it's, it's one, just where it's a multiply by select one none and the conditions.
So just specific for that.
Not, not all, not all muls.

**Geohot** [00:42:08]
I see.
Yeah.
I mean,
I don't know.
Half of me wants to say that TinyGrad doesn't support Nans and... Yeah, me.
Half of me wants to say that TinyGrad just doesn't support Nans and Infinity.

**Chenyu** [00:42:24]
That doesn't make sense.

**Wmped** [00:42:27]
Yeah, but do you mean for WebGP?

**Geohot** [00:42:32]
No, I mean for everything.
I hate Nans and Infinity.
Chenyu, why does it make sense?

**Chenyu** [00:42:39]
What do you mean by that?
That doesn't make sense.

**Geohot** [00:42:43]
It doesn't make sense.
Well, I just don't want to support them.
Nan and infinity don't work.

**Chenyu** [00:42:47]
Then your math doesn't math.

**Geohot** [00:42:52]
They're not even real numbers.
It's not even a number.
It can't be math.
It's not a number.

**Chenyu** [00:42:58]
What?
Of course, infinity is extended real number.

**Geohot** [00:43:01]
Oh, infinity.
Yeah, whatever.
If we can make it work with a bunch of hacks, we make it work with a bunch of hacks.

**Wmped** [00:43:20]
I can also like skip infinite and nan tests.

**Geohot** [00:43:25]
No, no, no.
If you could make them work, I'd rather they work.
alright good.
There's not too many if webGPUs around here.

**Wmped** [00:43:37]
Yeah, no, not.
So we had one in
And then init, it got removed with you moved the Dtype to device and that helped a lot with that.
I think the only only remaining if is I think for this KSI stuff for the buffers and no other precision issues gaps.
Yeah.
Cosign, sign, stuff like that.
Yeah.
Just not as precise.
In Metal, I see in the kernel that there is this precise sign and stuff like that.
You have the precise names with prefix.
I think in the WebGPU implementation it's just
for some reason, not as precise, but this is also a thing I want to.
I will take another look at the skip tests and see if I can pass more.
This is what I'm doing, is I can pass more and more tests and removing skips.
This is also a point where I have to look at there.
I just couldn't find the quick fix it.
It's basically I'm using the details and it's just not as precise for some reason.
Yeah.

**Geohot** [00:45:03]
I understand.
We'll get you 150 lines.
You can also disable sign if you want.
You can also use the transcendental rewrite for sign if it's not precise.
The transcendental rewrite will pass.
So if you just literally don't add sign to your code for op, you just comment out sign and you'll be like, wow, it works.
Actually, wait, you don't even have a sign in your code for op, do you?
C-style language, I don't think has sign.
Do you know if sign is actually being written as sign or it's being written as something else?

**Wmped** [00:45:50]
A C-style has sign, I think.

**Geohot** [00:45:55]
Oh, it does.
It does.
Okay, never mind.
Yeah, but you can take it out if you want.
Okay.
Try it.
If it's just sign.
But yeah, if it's just sign, also just skip sign.
Right now I see a ton of stuff being skipped.
I see all the unaries and binaries being skipped.
But cool.
I promise you 150 lines for WebGPU.

**Wmped** [00:46:17]
Okay.

**Geohot** [00:46:18]
And we will get.

**Wmped** [00:46:18]
Yeah, and I promise you a cleanup and export it to stable diffusion.

**Geohot** [00:46:32]
Sounds good.
I'll answer this question quickly.
You made a preorder for a tiny box, but now you want to buy a green one.
Your preorder does not specify a color.
And no, there's no EU headquarters.
There's no resellers.
You got to pay the import tax, right?
You can't get around the import tax.
If there's a reseller, they're paying the import tax, right?
You're always welcome, by the way, to ship it to somewhere in the United States and figure out how to get it into the EU yourself and not have to pay any duties and tariffs.
I don't know.
Yeah.
Also, if you want a green tiny box, buy quickly.
There will be more, but they may be out of stock for a month.
You know, just due to 4090 supply.
So, yeah.
FSDP.

**Chenyu** [00:47:25]
Oh, I saw that it's being closed.
That was a little question mark.

**Geohot** [00:47:31]
Oh, it's being closed.
That's news to me.
You know a lot more about it than I do.

**Chenyu** [00:47:36]
Oh, no, no.
The author closed it and say there was a better way to do it or something like that.

**Geohot** [00:47:44]
Cool.
So that's probably a better way to do it.

**Chenyu** [00:47:47]
Oh, I think we unlocked that one.

**Geohot** [00:47:49]
Unlocked.
Unlocked in the spreadsheet.

**Geohot** [00:48:03]
T.J. Becker doesn't happen to be here.
He's making good progress on the big DFA for pattern matcher.
I did a whole bunch of clean up work to make everything faster.
It was nice to see it reflected in stats.tinygrad.org when I run it up on stream.
You can see how like...
It's running down again.
Yeah, that's good.
Good things are moving in the right direction.
Well, things are turning a little bit back off, but...

**Chenyu** [00:48:36]
Yes.
It's hard to believe there was once for Unjitted Llama.
It was once below 100 milliseconds.

**Geohot** [00:48:48]
Uh, never on a tiny box.

**Chenyu** [00:48:50]
Yeah, but there's no tiny box when that was fenced.

**Geohot** [00:48:56]
Yeah.

**Chenyu** [00:48:58]
I mean, the Mac one, Mac is 700 now.

**Geohot** [00:49:02]
Yeah, that used to be 100 milliseconds.
That's kind of crazy when you think about how to get so slow.
that's 7x slower.
We'll get back there.

**Chenyu** [00:49:11]
Tensor cores?

**Ignaciosica** [00:49:26]
Hello?
I opened a draft PR earlier this morning showing the progress, but I don't know how much overlap is with Quasling work from what she said today.
So I'm waiting and still working on it.

**Geohot** [00:49:38]
Does this swizzle pass?
Where is the swizzle?
I see fix up AST.

**Qazalin** [00:50:01]
Yeah, I am I'm working on a swizzle rewrite but I read your diff quickly like it just came through us.
I think it's fun But if you want a mergers, I can handle any
conflict that can happen with my work and eventually like measure everything into a unified swizzle.

**Ignaciosica** [00:50:34]
Okay, so I will clean it further and open the PR.

**Qazalin** [00:50:41]
Yeah, just one thing is like you have cast and stuff like you don't really need to do all those like the pattern measure for the cast is just too specific.
It's just any elementwise can go there.
Yes.
Yeah, I think your diff can be smaller.
It can share some stuff with the scheduler.
But other than that, there's some other cleanups.

**Ignaciosica** [00:51:10]
The thing with the... Sorry.
For the views, is that here the parent view is replaced the child view?
That was the question I had like two weeks ago.
That difference from the schedule where the child view has preference over the parent view.
Well, the child view is split, right?
So you can use one or the other.
OK, I'll check that.
And in the merging, I think, I'll take a look.
I need to clean the rules, yes.

**Geohot** [00:52:08]
I'm trying to figure out where this view is being created.
Oh, there it is.
Oh, I see.
Yeah.
OK, I see.
So sources, if TC pattern and sources,
has st sources sub i dot fix dot view.
Oh, I see.
Cool.
I mean, yeah, I know overall, I think it definitely looks cleaner.
And I think, yeah, with a bit more.
I'm so happy that applied to S2 things gone too.
OK, cool.
Yeah, I think with a bit more cleanup, I think this is good to merge.

**Ignaciosica** [00:52:39]
OK, thank you.

**Geohot** [00:52:41]
Cool.
Is there progress on match speed?
Oh, the matching engine speed.
Oh, yeah.
I mean, I think I gave that more as a contract to TJ Becker and I think he's making some kind of progress on it.
So yeah, I don't know.
I don't know if we have numbers of the speed, but it's a very fun standalone problem.
If P2P hack is patched on 5090, will it delay the upgrade of tiny boxes to 5090?
There's currently no plan really to do a 5090 tiny box.
There will probably be a 5090 tiny box pro, but
One of the problems with the 5090 is it draws 600 watts.
You're just running into a real problem.
Whereas how many power supplies do we want to put in this thing?
Is it going to be a three power supply machine?
I mean, it might have to be.
We have some stuff for a tiny box with PCIe 5.
We've played with the new Asrock motherboard, but yeah, there's no rush to go to 5090s and go to PCIe5 for the tiny box.
It's going to be if you're banking on that anytime soon, don't.
We're going to be selling basically the same tiny boxes for a year.
We have a lot of those motherboards.
No, I don't like the idea of being at lower clock speeds.
We support full power.
We don't support it at all.
We'll build some prototypes.
But there's no rush.
We're not trying to be first to the 5090s.
If you want to be first to a GPU, you're overpaying for it.
And I hate overpaying for things.
So if you want a good, solid machine learning machine,
Comma is standing up another 18, 4090 machines.
The 4090 is the well-trodden path.
In a year, 5090s will be good.
But I think for the next year, it's going to be 4090s.
I'm not playing with MSRP and scalpers, right?
I'm waiting until I can go to a supplier and say, I want 200 of these.
So yeah, it's not like we have something like on day one when the 5090 comes out.
Oh, site guys, it's the tiny box too.
We have a prototype with the PCIe5 motherboard just so we could update the case.
But at 600 watts, there's no way.
We're going to be able to do it quickly.
Maybe we'll put four GPUs in it.
Would you be happy with that?
Would four GPUers be happy with four GPUs in the tiny box town?
All right.
Any other tiny grad related questions?
If you want to just buy a normal, buy a normal, buy a normal computer.
We also do not know anything about the signal integrity of PCIe5.
Getting signal integrity to work for PCIe4 required PCIe5 stuff.
So I have an idea that getting PCIe5 to work is going to require PCIe6 stuff.
I'm never selling a computer that has any AER errors.
Uh, okay.
Okay.
All right.
You're off in, you're off in loony.  You're off in loony land.
Are you talking about phase change, cooling and PCIe switches?
Loony land.
Yeah.
And MSRP, $150,000.
Um, how many of those do you actually built?
The 8x 4090s.
But you built 300 8x 4090 boxes.
And you used phase change cooling.
Oh, 340 90s.
Oh, that's not crazy.
That's that's that's common scale.
You went with phase change cooling for that.
Inference provider.
Cool.
I didn't realize, by the way, I misread your thing.
I thought you were suggesting that I do that.
I didn't realize you actually went and did that.
Actually going and doing that is cool.
Telling me I should do it is like, I'm not doing that.
I'm not touching those.
Do you want to talk about it?
I'll make you a speaker if you want to talk about it.
If you rejoin and, if you rejoin Red's only VC, you can speak.
You need 5090s for training.
Why, what do you know about 5090s?
Let me get my head set going.
Sorry.
Sure.
No worries.
That's most that's most of the meeting, which is this is just the GPU shit talking hour now.
For us to do anything else.
Oh, sorry.
No.

**Chenyu** [00:59:11]
Oh, ML perv will be out this week, I think on Wednesday.
We should see.
I think the spotlight is Google Trillium.
I think their training time is a lot better than the V5.

**Geohot** [00:59:26]
What is Trillium as hardware or Trillium as a?

**Chenyu** [00:59:29]
Trillium is hardware.
It's V6, kind of.

**Geohot** [00:59:33]
Oh, it's the V6.
It's the V6 TPUs.
Yeah.

**Chenyu** [00:59:36]
Yeah, it's like three times better than V5P.
It's the one that made NVIDIA nervous.

**Geohot** [00:59:49]
Yeah, what are they going to sell them?

**Chenyu** [00:59:52]
They are not going to.
It's in preview.
Supposedly you can use cloud to access those.

**Geohot** [01:00:03]
Someday we should work on adding TPU support to tiny grad.
That will be.
I can output that up with the TPU instructions.
Alright, back to GPU should talk again, but you know it will for Wednesday.
That's exciting.

**Bghira** [01:00:25]
Here's a picture of the PCI five switch that we developed with for run where it's our internal inference hardware.
So we can use 4090s at their full lane width.
We're not using like high core count GPUs or anything like that.
So actually when we switch over to an H100, our speeds drop because the H100 is SSXM5 and therefore locks you into a specific hardware configuration and none of it's as fast as what we've been able to put together.
So that's why I've been looking at the 5090s.
They have 32 gigs of VRAM each so that I can fit more layers onto each device before having to do some stupid shit like FSDP or deep speed, something like that.

**Geohot** [01:01:11]
Wait, so are you... I see six lanes there.
I see six slots there.

**Bghira** [01:01:20]
This is one of our earlier prototypes.
So there's one with eight that actually slots in.
And then I don't have any pictures on hand of the hot swap stuff or phase change cooling.

**Geohot** [01:01:31]
Which chip did you use?
Microchip or Broadcom?

**Bghira** [01:01:35]
It's microchip.
And nobody had actually used this one before.
And we knew that because their hardware spec was wrong.
So we weren't able to get it to work for a month.
And then we had to work with them.
And one of their pins was disabled.

**Geohot** [01:01:47]
But it's the, it's the PCIe five one then, if you're doing eight.

**Bghira** [01:01:51]
Yeah.
It is.

**Geohot** [01:01:54]
Ah, okay.
Cool.
Yeah.
Yeah.
No, I'm very familiar with all the PCIe switch lineups.

**Bghira** [01:01:59]
Um, so we have improved their documentation for that one.
So hopefully if you get into it, then it'll already work for you.

**Geohot** [01:02:09]
Um, my conclusion on PCIe chips.
is that you're never going to find a cheaper PCIe switch than AMD Epic CPUs.
How many did you connect to?

**Bghira** [01:02:23]
So what do you mean, the clock right?
So, at risk of giving away some internal info, we do find that the CPU clock frequency greatly benefits text image inference speeds, so that when we're using, let's say, a 5800X3, 7800X3, or 7900X,
The X3 in the 7800 series wipes the floor with the 5800 and then the 7900X does the same to the 7800.
But now I'm waiting on the 9800X3D to see if the chiplet configuration redesign improves things.
But I wasn't able to get good performance from Xeon or Epic or anything higher end data center grade because they're just lower frequencies.

**Geohot** [01:03:10]
Wait, you're using like Ryzen chips?

**Bghira** [01:03:14]
Yes.

**Geohot** [01:03:17]
Ah, yeah, no.
So the GPU performance really shouldn't at all be bottlenecked by the CPU.
Like our Nvidia driver will completely decouple these things.
Our Nvidia runtime.
I know the normal Nvidia runtime doesn't.
But ours completely decouples the CPU time from the GPU time.
But okay, I mean, that's also a way to get like, cheaper I guess

**Bghira** [01:03:39]
We're able to compile everything into a single graph and send it to the GPU.
But even then, the H100 system is just bottlenecked on.
I don't know what exactly.
I haven't dug too deeply into it.
All I saw was that the cheaper system outpaced it.
So I just went with it and didn't bother to check into why.

**Geohot** [01:03:58]
I mean, for single core, for single core, like ryzen is so fast.
I mean, not as fast as M4, but.

**Bghira** [01:04:08]
Yeah, but I can't get an external GPU on an M4 device, even though I'd love to.

**Geohot** [01:04:15]
Where one of the things we've talked about for comma a bit is building a, it's obviously not going to have bandwidth, but building a USB to PCI adapter.
And then we can sell AMD GPUs connected to MacBooks.
You'll be able to just buy a 7900 XTX, plug it in using one of the... You can use those NVMe to PCI, NVMe to USB things, plug it in with that.
And then if TinyGrad has a complete driver, we can actually run it.
By the way, Nimlgen, if you're still here, this is probably where the AM driver is eventually going.
I want to be able to run GPUs over USB in order to, for the next gen Comma devices, get, plug in the AMD GPU.
Why not Thunderbolt?
Because the Comma devices don't have Thunderbolt.

**Bghira** [01:05:20]
And nothing can really give us that full memory bandwidth of the 4090 anyway.
I'd be interested in finding a way to get that, but that's like card redesign territory.

**Geohot** [01:05:34]
Oh, you mean to stream it out?
You mean to stream like to get more than the PCIe bandwidth?

**Bghira** [01:05:39]
Yeah, because it's not even PCIe 5 capable.

**Geohot** [01:05:43]
Yeah, yeah.
Yeah, we'll see.
You'll see.
I haven't seen PCIe5 work on anything yet.
Everything I've seen with PCIe5, I've tried a bunch of the PCIe5 SSDs and they're flaky.
I haven't seen anything actually work at PCIe5 speed yet.

**Bghira** [01:06:00]
And I'm hoping it's just a documentation issue where a pin was mislabeled on something like I ran into.
That'll get fixed real quick.

**Geohot** [01:06:10]
I'm not sure it's that.
I think the problem is all of these motherboard manufacturers didn't have any PCIe5 things to test with.

**Bghira** [01:06:18]
Oh, chicken and egg.

**Geohot** [01:06:21]
Yeah, exactly.
So like these GPUs are going to come out, but it's going to require another gen of motherboards before they work.
I don't know, just a theory.
Any thoughts on the USB AMD if our driver is going to work with that?

**Bghira** [01:06:40]
Yeah, if you can compile everything and then offload it to the GPU so that it runs solely over there, that should work.

**Nimlgen** [01:06:49]
So yeah, I mean, the only thing we need right now is just to map the PCIe regions.
So I mean, yeah, if we just can talk USB to the GPU, so everything should work.
I mean, on any platform.

**Geohot** [01:07:06]
Oh, yeah.
Wait, yeah, you're right.
As long as, yeah, this should be totally dealt with at a different abstraction layer.
We just need to be able to, yeah, like, like, mmap the USB.
We looked a bit into those NVMe chips and they were kind of annoying, but there's some FPGA solutions for this too.
I love the idea of being able to plug an AMD GPU in over USB to anything and then having tiny grad run on that.
Wow.
This is actually doable now.
That's exciting.
Yeah, just like, mmap the GPU.
Do we have to blacklist the kernel driver on startup, or can we unload it?

**Nimlgen** [01:07:57]
No, we should definitely turn off the driver or just unload it because running them in parallel
We'll just kill the GPU because driver also just trying to do something on the GPU in the background.
So yeah.

**Geohot** [01:08:16]
It works.
It works either if we don't load the driver at all, or if we unload the drive.

**Nimlgen** [01:08:21]
Yeah, yeah.

**Geohot** [01:08:23]
Great.
Cool.
Let me do a cold init.
Yeah, for the go back to the
300 4090s DC, I'm too lazy to do PCI switch hardware.
We're just like, what's the cheapest way to do this?
If you saw the way we did it in the TinyBox Pro, I just took the fans off, and then mounted the cards vertically, and then just pull the air through.

**Bghira** [01:08:50]
The HP approach.
They do it in all of their DL servers.
They just force air through everything.

**Geohot** [01:09:05]
Yeah, yeah, it was just like the GPU, like the heat sink is a great heat sink.
You know, the first thing we did, we actually made a custom heat sink to go on 4090s.
And we're like, oh, we can put these in servers and then like the normal server fans will work.
But they only got like 350 watts.
We couldn't get like 300 350.
So I don't know if we just did it wrong.
I think we only had heat pipes.
I'm not sure we had a vapor chamber.
Cool.
Anything else?
Any other questions?
Let me just check the chat if anyone posted in here.
Would TinyBox owners ever be able to connect to their boxes with Cloud equals one?
Yeah, you can already set that up today.
Um, you can just like just SSH channel a port that'll actually work right now with what I just merged.
You watch me do it.
You watch me do it.
I just did it live on stream.
Um, so if you just on your tiny box, if you run, uh, the Python tiny grad runtime ops cloud, uh, and then you forward port 6667 to your computer, just run with cloud=1 in middle work.
Um, see it can hit your tiny box.
Will there ever be a tiny book?
No.
No.
I believe in selling the full, I believe in like vertically integrating, but then selling every piece.
So we may sell PCIe cards.
We might even sell chips.
I don't know about, we'll see about chips, but PCIe cards I'd love to sell.
Like a thousand dollar competitive card with Nvidia.
So you'll be able to get a tiny, and then I'll make USB versions of that too, or ethernet versions, like I don't care what they're connected with.
Maybe it won't even be a PCIe card.
It will just be an ethernet appliance.
It'll be like a NAS.
Remember those like QNAP NASs?
We'll have a QNAP NAS, but you just do that for deep learning.
It's just not a computer.
You just talk to it over ethernet for many of your things.
It supports like the cloud protocol or something.

**Chenyu** [01:11:28]
We can print the source code of TinyGrad and make it a tiny book.

**Geohot** [01:11:32]
We did this.
We did this at comma.
We printed the weights of one of our models and got it bound into a 500 page book.

**Chenyu** [01:11:42]
Well, TinyGrad solves for a bit more interesting to read than that, I'm sure.

**Geohot** [01:11:47]
Pretty good weights for a bottle is the only way to copyright.
uh yeah yeah the tiny grand book tiny book who would buy that let's let's get it on amazon let's get a publisher wait i think we have to fix there's a few lines that are still longer than 150 characters we'll have to figure out how much uh we could like is 150 character width reasonable for like a book page i want like beautiful syntax highlighting in our book too i want it to be a beautiful book
All right, we're in.
We have real questions about tiny grad.
What do we have left?
The weak value dictionary is slower than a normal dict.
Yeah, I'm aware.
But if it's not weak value, then how do you ever free uops?
I'm not even sure Uops are being freed.
There needs to be a lot more testing around that.
Also, weak value dictionary is just particularly slow.
We used to have a custom version of it that was rewritten to be faster.
Yeah.
I don't know.
Just use the jit.
No, there won't be tiny books.
We're never making laptops, okay.
This is not laptop company.
Although our chip might be used in comma devices.
So that's kind of that.
I think the first chip we're going to do hopefully is a chip the comma can use in like the comma five or something.

**Chenyu** [01:13:50]
Oh, now we are on 3.10, we also need to upgrade the... I believe one of the CI machines is on 3.9.

**Geohot** [01:13:59]
Oh, is it failing?
It passed.

**Chenyu** [01:14:02]
I don't know, but if it's on 3.9, we need to upgrade it.
Otherwise, it will fail someday.

**Geohot** [01:14:10]
Yeah, yeah, yeah, agree.
We're committed to 3.10.
Figure out which CI machine it is.
Is Pallas okay for TPU backend?
No.
No, I want to generate TPU assembly code.
I mean, this is kind of it.
Pallas looks very much like Triton.
Pallas is actually Triton.
Really?
He has a Triton like bomb.
Triton's flavoring has good docs.
The problem I always run into with Triton is, like, you get off the happy beaten path, and then Triton gives errors or is really slow.
You guys tried to write back end, Triton back end, so you try to grab a whole bunch of times, and then over fast.
or they, well, you can, yeah, you can either write the ones that have errors or the ones that aren't fast.

**Bghira** [01:16:03]
Yeah, there was a hackathon at the GPU.
It's going to say there was a hackathon at the GPU mode conference and we rewrote flux entirely and Triton and it was slowest and PyTorch compile was.
Yeah.

**Geohot** [01:16:21]
Yeah, sometimes it's just slow.
Like to get speed from Triton is not easy.
You have to like write it in the special way that the thing is happy with.
I mean, my understanding of it is mostly like MLIR and a bunch of different stuff.
Cool.
Any last things?
TPU v6, of course.
I want to support the latest TPU.
I mean, I think a lot of them are pretty similar.
The reason I'm interested in supporting TPUs is because there's a chance our hardware is going to look a lot like TPUs.
Google's made a lot of the trade-offs correctly.
I have a document I don't know if it made a public where I went through and like analyzed all the trade offs that all the different companies are making.
And I think Google's got most of the right.
The main problem with GPUs is that they aren't for sale.
uh isn't there gaudy three isn't there gaudy three now um my thoughts on gaudy is it looks it looks like it's basically just built to do matmals uh i don't even know if it can do like convolutions and stuff fast two is very barely available three seems like a fantasy that's too bad
They can't you build these things?
There won't be any gaudy for they sack the line up and classic Intel.
Build something.
People might be interested in it.
What do we have to do?
Well, I don't know cancel it.
Wait, they actually saw there.
Where did you hear that that there won't be a gaudi for?
So Intel is so, so sad.
Well, just the lead left doesn't mean, I mean, maybe that's widely left.
You know, what the tiny cloud might end up using.
There's a MI350x.
There's a world in which we end up using the big, if we manage to successfully build AMD driver stuff and fix all the jankiness of AMD, there's a world in which the tiny grad cloud is actually the enterprise accelerators from AMD.
We'll drag them across the finish line, whether they want to be dragged or not.
Oh, man.
Running our driver with the USB is really exciting.
Do I suppose 100% of the VRAM?
Oh, is there something weird about the VRAM on this?
I saw some benchmarks that were just horrendous for the MI 350.
With some of the RAM is banked weirdly or something.
It's bad.
Yeah.
Of course.
I mean, how much of it is software though?
Like, like how much of these bugs exist in the hardware and how much of this is just like their hardware team's actually gray and they just wrote clown software.
It's all software.
I know, I know.
Hey, is Intel, is AMD ever going to?
This makes me not want to fix it.
This makes me like, like, like AMD come to me and be like, we are serious now.
We actually want to fix this, but they will.
Maybe you've been finding the people who are getting laid off from Intel.
Import, AMD extensions for PyTorch.
Yeah, try a TPU as a backend.
I think we have a lot to do before we get to a TPU as a backend.
I think TPUs are one of the most aggressive ASMs.
When you think about assembly, even GPU assembly, the least aggressive, the easiest ASMs to do are going to be CPUs.
If you're doing like ARM or X86, it's actually pretty easy to get performance out of these things.
I don't know why the performance is so bad of LLVM right now.
I really think that I'm just not enabling the right, oh, we need to enable the optimized pass.
Of course, it's one of the six ways to enable it in LLVM light.
But no, I think we have a lot to do before we could merge a TPU assembly backend.
I think like there's LLVM IR and then there's CPU assembly and then there's GPU assembly, then there's TPU assembly.
Is assembly LLVM actually vectorized?
Yeah.
Yeah, LLVM will vectorize for you.
Oh, I added also you can do LLVM opt equals one and it'll run an LLVM optimizer, but it didn't get as much speed as I thought it would.
I don't exactly understand why the gem Vs are as slow as they are.
I don't know.
Now I'm trying like gemm on my entry max and they're slower than I thought.
OK, cool.
This meeting's already run way over.
Thanks, everyone.
See you all next week.
Bye.
Bye.

