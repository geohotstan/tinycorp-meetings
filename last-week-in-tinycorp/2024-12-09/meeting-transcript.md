# 2024-12-09 Meeting

### Meeting Agenda

**Time:** 9:30 AM San Diego time (PST)
- Delete lazy!!!
- Things after delete lazy
- Cloud sprint
- AM driver
- WebGPU
- Bounties (onnx, tensor cores, add chain symbolic)

### Audio

[Recording](https://drive.google.com/file/d/1SEZzdQqpQzfjf6b1vZcWjVGsXqzX0Igh/view?usp=sharing)

### Chapters

- **00:00:00 Delete Lazy Priority**  
  Deleting lazy is the top goal this week!

- **00:02:28 Fixing GC**  
  Geohot takes charge of garbage collection fixes and Qazalin works on optimizations.

- **00:06:26 Gradient Refactor & Speed Goals**  
  Talks about making CIFAR and LLM faster.

- **00:09:01 AMD Drivers & USB GPUs**  
  Updates on AMD driver progress and plans to plug GPUs into Macs.

- **00:16:00 WebGPU Upgrades**  
  Moving to Dawn for better support and making exports easy for everyone.

- **00:22:28 TensorCore Swizzling**  
  Improving TensorCore handling by swizzling stores.

- **00:28:31 Symbolic Chains**  
  Progress on new Symbolic bounty.

### Transcript

**Chenyu** [00:00:00]
Okay number 48 so we switch to this time.
Do you want to do like different time earlier or later?

**Geohot** [00:00:11]
This time's fine 

**Chenyu** [00:00:00]
So we start with delete lazy because delete lazy is important 

**Geohot** [00:00:19]
Yeah it's getting merged like today or tomorrow or definitely this week we're gonna force it through even if it breaks everything!

**Qazalin** [00:00:35]
No, it's not going to break everything.
It's actually correct.
Everything is correct.
Objectively correct.

**Geohot** [00:00:45]
GREAT!
Can I click merge?

**Qazalin** [00:00:47]
Oh my god, GC is so annoying.
I don't know how to fix GC, to be honest.
I probably spent so many hours on it.
I don't know.

**Geohot** [00:00:58]
Yeah, I mean, it's not obvious.
I don't have an obvious solution either.
I think..
What we can try now is we can just ref count the tensors to know if a UOP is referenced by a tensor.
And if a UOP is not referenced by a tensor, at the end of the schedule run, we should free all of the ones that have the buffers.
The buffers of the UOP with ref count zero.
So the graph, the UOPs itself, might live forever, but the buffers won't.
And it's the buffers that are OOM-ing, not the graph.

**Qazalin** [00:01:36]
But what do you do about like the intermediate buffers that we realize?

**Geohot** [00:01:41]
The intermediate buffers that we realize are totally fine.
You only trigger this actual deletion after the scheduling is done.
So like when the ref count gets to zero, we add it to like a buffers to be cleaned up thing.
And then after schedule returns and all the run happens, 
how do we mute that by the way?
Do you know how to mute that?
Okay, I'm not going to mute that.
Yeah, so you see what I'm saying?
Does that work?

**Qazalin** [00:02:19]
I don't know.
You ref count on the tensor.

**Geohot** [00:02:28]
You know what?
I'll take care of GC.
I'll take care of GC this week.
I think I have a bunch of things to try.
It's not obvious.
I don't think you're missing the obvious right way to do it.
I'm kind of spitballing.
I'm not 100% sure what I'm saying is right.
Is there anything but GC left?

**Qazalin** [00:02:52]
No, I fixed pickle today.
Compile3, the diff doesn't exist.
Everything else should be good to go.

**Geohot** [00:03:04]
Right.

**Chenyu** [00:03:07]
Is the test indexing by a const thing a problem?
Is that a regression?

**Qazalin** [00:03:14]
I think everything I get is a optimization problem.

**Geohot** [00:03:21]
Oh, yeah, but we have to get those back in.

**Qazalin** [00:03:24]
Oh, yeah, sure.

**Geohot** [00:03:27]
Deleting the optimizations was just a temporary thing, because now we can add them back.
You shouldn't let optimizations.

**Chenyu** [00:03:34]
It's not optimization.
I remember seeing one test in test indexing that was previously passing, and now it changed to check race assertion.

**Qazalin** [00:03:47]
Oh, that one, I'll look into it.
But everything should be, like, nothing is correctness.

**Geohot** [00:03:53]
Cool.
Yeah, so let's maybe, you start adding back optimizations, and I will fix GC.

**Qazalin** [00:04:00]
Great.
Yeah, that sounds great.
Actually, merge ops folding, reduce folding stuff.

**Geohot** [00:04:10]
You mean my stride zero stuff?

**Qazalin** [00:04:13]
Not your stride zero.
It's only for const, but I can merge your stride zero stuff next.

**Geohot** [00:04:19]
We can do stride zero later.
No new optimizations.
Let's just not regress.
Sorry, go ahead.

**Qazalin** [00:04:26]
Okay.
I'll get the elements-wise stuff with the const merged.
And then it's like ops folding is going to do merge views early.
I want to do that first.
That's very important.
And I also want to do that.

**Geohot** [00:04:44]
I changed my mind on that.
You don't have to do that if you don't think that's the right path.

**Qazalin** [00:04:48]
Oh, obviously it's the right path.
Oh, my god.
It's so easy to reason about the big graph when.

**Geohot** [00:04:54]
Great, great.
If you think it's the right path, then by all means do it.
But if you don't think it's the right path, I'm not going to hold you to that implementation.
But cool, yeah.
No, I like early ops folding.
Great.
Okay.
You work on optimization.
I'll work on GC.
I mean, the GC is all just poorly tested.
Everything is just kind of like.. So, I'll leave it at that.
Also, the first thing I'm going to do this morning is get rid of compile tool as well.
So, yeah, I agree that that thing that it was doing there is weird.
But also, any small PRs that you can pull out and get merged would be great.

**Qazalin** [00:05:33]
Yeah, if you look at the diff, it's pretty much like everything that UOP lacked, that Lazy had, like buffer and stuff like that.
It's mostly like filler.

**Geohot** [00:05:42]
We can start adding those things in with tests, like the features of UOP, into master.

**Qazalin** [00:05:52]
Okay, with tests.
Yeah, I think that makes sense.

**Geohot** [00:05:56]
Yeah, with tests, it tests the functionality and kind of like a stack.

**Qazalin** [00:06:00]
Yeah, I was sort of like, OK, if I merge, this is actually dead code.

**Geohot** [00:06:06]
I think it's fine as long as it has a test.
It's OK that it's not used anywhere else yet.
Again, deleting lazy is the most important thing right now for this whole company.
So let's get it done.

**Chenyu** [00:06:20]
Great.
Things after delete lazy.

**Geohot** [00:06:26]
Uh yeah I mean I got the gradient refactor I'll do that uh yeah derivative stuff 

**Chenyu** [00:06:38]
yeah so for now we have the function will become the new gradient stuff and we will start working on things like for now so uh sigmoid has its its own thing and that should be a rewrite.
I mean the gradients of that could be cleaned up, and we should be able to do a lot of similar things on other functions.
So the goal here is probably just training LLM that has the attention, has the softmax.
And we want probably also related to the conv backward.
We want the backward of these to be like a clean form.
And we know how to test those things.
We have things that we know is slow that shouldn't be slow.
Probably focusing on our CIFAR, or LLM.c, or maybe just ResNet and bigger ones.

**Geohot** [00:07:34]
The CIFAR is bad.
The CIFAR is 3x off torch and why?
I think making CIFAR good is really important.

**Chenyu** [00:07:44]
I mean, CIFAR is just a smaller version of ResNet.
And LLM.c is a smaller version of BERT.
So we have a new gradient API.
And I think a lot of Fuse Arange and a conv backward thing would just become the rewrite rule and we'll figure those out.
And indexing.

**Geohot** [00:08:06]
Yeah.
We got to figure out why our LLaMA is slow later.

**Chenyu** [00:08:10]
We need to first.. Measure it? is it really slower?

**Geohot** [00:08:16]
I think it is.
I don't think it slops either.

**Chenyu** [00:08:23]
Because our LLaMA 7B for the first 10 tokens is faster.
But we never test things like 200 tokens or something.
And that's noticeable slower once you start to use TinyChat.
Yes.
We'll fix those as well.
Oh, we probably don't have time this week for a cloud.

**Geohot** [00:08:41]
No, cloud's not happening this week.

**Chenyu** [00:08:44]
So cloud is not happening this week.
We will talk about that later.

**Geohot** [00:08:48]
Well, we'll get AM driver merged this week.

**Chenyu** [00:08:52]
Okay.
I don't.. Let's.. Okay, Nimlgen can start with AM driver, then we can talk about merging that later.
Yeah.
How's AM driver going?

**Nimlgen** [00:09:01]
Yeah, so got p2p and interrupts working for AM.
So, yeah, from the point of view of feature, it's just complete.
I'll optimize some line usage.
So yeah, but I think it's 600 lines, because now we have SDMA and interrupt stuff on the GPU.
So yeah, it's pretty big.

**Chenyu** [00:09:30]
Do we keep AMD?

**Geohot** [00:09:32]
You have to, yeah.
It's not that much more.
How many more lines is AMD?
Like, if we were to rip out the thing that interfaces with the kernel driver.
I'm not saying we're going to do it, but.. 

**Nimlgen** [00:09:42]
So, no, I mean, AMD is.. So, currently it's, like, plus 100 lines, but that's actually.. Like, the interface to communicate with GPU directly and interface with KPD, each of them is 100 lines.

**Geohot** [00:10:05]
Wait.
Oh, you mean it's 100 lines to communicate with the GPU directly, but that doesn't include the 500 lines that basically bring up boilerplate?
Is that what the other lines are?

**Nimlgen** [00:10:13]
Yeah, yeah, yeah.

**Geohot** [00:10:17]
Yeah.
I want to get the hardware interface stuff merged too, where we can abstract out.. I don't want to abstract.
I don't want to test at the layer.
I want to test at the syscall or memory layer more than I want to test at this abstraction layer.
But by syscalls, I mean open-close kind of thing, not like..
whatever function you've defined that's shared between the kernel driver and the direct driver.

**Nimlgen** [00:10:51]
So we want to keep this, not to keep, just to bring this, like, file interface, which you called hardware interface, like, to open file, like you could tell it.

**Geohot** [00:11:06]
I think so.
Yeah, I think that's the right place to test.
I mean, I'm open to, if you think something else, I'm open to, I'm not sure, but.. 

**Nimlgen** [00:11:17]
Yeah, okay.
I mean, we have, it would be pretty annoying because we have, like, right now with syscalls and integrate seamlessly, so there is, like, syscalls to iterate directories, which is needed for AMD.
to kind of support multi-GPU.
So it will be annoying, I think, to create interface for that as well.
But yeah, I mean, it's just a lot of lines.
It's just not really annoying or something, but yeah.

**Geohot** [00:11:49]
I mean, you know what?
Forget about, like, I won't specify a way to do it, but what I want to do is be able to run these things on Mac.

**Nimlgen** [00:11:59]
Mm-hmm.

**Geohot** [00:12:03]
What's that going to take?

**Nimlgen** [00:12:08]
Yeah, I mean, it's OK, I think.
Yeah, but it's a lot of to support for Mac, especially all these directors, because currently it's just all these dentures, which is Linux specific.

**Geohot** [00:12:20]
Yeah, like that's what I'm saying.
Like, I would like whatever this hardware interface or file interface abstraction to be to be kind of platform independent.
Like, I want all of the Linux, Mac, or Windows-specific stuff abstracted into a class.
And then, like, I want the test to work on all of them.
And then the Direct stuff.
The biggest thing that I'm excited about about the Direct stuff is.. So, Comma has a Snapdragon 845, and we want to plug an AMD GPU into that.
We have a USB port.

**Nimlgen** [00:13:03]
Yeah.
Right now, it's kind of abstracted.
All this GPU setup, you just pass, like, three memory views, which is, like, doorbells, VRM, and all that.
And I just set up GPU using these memory views.
So, and OpsAMD has all this, like, interface to set up VFIO and interrupts and actually map these PCIe regions.
So, it works.
So, it's kind of abstracted already.

**Geohot** [00:13:37]
Yeah, I mean, we're going to buy a couple.
I got to order them today.
We'll buy a couple USB to PCIe adapters, and we'll see if we can get them working.

**Nimlgen** [00:13:49]
Yeah, sounds cool.

**Geohot** [00:13:50]
I mean, I think it's also an awesome product for TinyGrad.
I'll send you one once we have them to get a 7900XTX working on a USB port on a Mac.
like that's you know people are always like oh when is what is tinygrad when is tiny corp gonna sell something that's like a thousand dollars and like it's not something that's a thousand dollars it's an external gpu for your mac!
But yeah, no, just so we basically need the test working.
I have some bounties up for them available to anyone here to get basically gpuocelot.
But maybe remu is easier.
Remu, I'm sure, is easier to get that working on Mac.
I want the tests to work on my machine, basically.
So whatever abstraction we put, I want this abstraction to be, I want it to basically have two things.
One, it shouldn't be a, the abstraction should be as close to the metal as possible.
I don't want it to be an internal abstraction that we have to maintain.
The thing about open and close is we didn't make those abstractions.
And two, I want it to be platform independent.
So what's the furthest down we can go that's platform independent?
And then same thing with the direct thing.
It's like, what's the furthest down we can go?
VFIO is a Linux abstraction, but like interrupts in memory are not.

**Nimlgen** [00:15:21]
Yeah.

**Geohot** [00:15:24]
I know for the memory we use libPCI access.
That's what should be abstracted in our hardware interface class.
And it should be the same hardware interface class.
It shouldn't be two types of classes.
There should be one that just says hardware interface, open, close, map, so on and so forth.

**Nimlgen** [00:15:41]
Yeah.
Sounds good.

**Geohot** [00:15:44]
Cool.
Yeah.
Hal.
I think I called it Hal.
I don't know.
Whatever you want to call it.
It's like, yeah.

**Chenyu** [00:16:00]
I don't know.
How do we find 600 lines?

**Geohot** [00:16:05]
I don't know.
I don't know.

**Chenyu** [00:16:08]
We'll see where we are after.

**Geohot** [00:16:10]
Yeah, delete lazy.
Yeah, delete lazy is going in.

**Chenyu** [00:16:14]
OK.
Sounds good.
The next is for WebGPU.

**Wpmed** [00:16:22]
Yeah, so last week I got rid of WebGL.
I fixed some atomics in SMEM and some atomic load issue in Chrome.
I removed F16 to F32 GPU JavaScript and replaced with TinyGrad code.
I also deployed the YOLOv8 demo.
I moved WebGPU tests to Ubuntu and worked on property types in the exported WebGPU model because it was always float32 regardless of the actual input and output types.
And yeah, the F16 stuff is partly done.
So there is this unpack and pack built-ins that I can use.
Actually, the currently deployed YOLOv8 that I deployed today is using this unpack.
So it unpacks F16 weights to F32.
And so the page loads faster, but the performance is about the same.
But this week, what I want to do is add real F16 support.
And I think for that, I probably have to switch to the Dawn WebGPU engine because it supports it.
And F16 is supported in Safari.
I tested it.
So it's supported anywhere except for the wgpu lib we are using currently.
And there is a PR for it that's open for about seven months now.
So I don't see it getting supported in the near future.
So I think it's just easier to switch to this Dawn engine.
And then..
The YOLOv8 be faster and also a stable diffusion will load faster and will be faster.
We don't have to do the decompression stuff and things like that.
Yeah.
And then also there's this.

**Geohot** [00:18:26]
Does Dawn not have Python bindings?

**Wpmed** [00:18:29]
I don't know, but I will provide Python bindings.
I think we can generate the bindings.
as we do for other libs, like this autogen style I think will work.

**Geohot** [00:18:41]
I see.
So we can use autogen basically on their WebGPU.c.

**Wpmed** [00:18:44]
Yeah.
That's what I'm planning to do.
I think it's..

**Geohot** [00:18:52]
This project's well-maintained, this Dawn project?

**Wpmed** [00:18:54]
Yeah, it's in Chrome.
So Chrome, it's a Google's engine.

**Geohot** [00:18:58]
Yeah, I think that's a good move.

**Wpmed** [00:19:01]
Yeah.
I really like the library we're currently using.
It's just that there is the Python interface that's a separate repo, and it sometimes lags behind the actual underlying Rust library.
But they are responsive.
So the timeout issue I filed last week, that got resolved.
They removed it because they realized it wasn't really needed.
And they said they will release it tomorrow, so we can bump the version back to latest.

**Geohot** [00:19:33]
No, I think moving to Dawn's a good idea.
I like this, like, it's the WebGPU IDL.
I mean, Chromium, like, web standards?
We just have Chrome.
So, yeah.
Cool.
Yeah, I like that move.
I think also, like, two goals for the WebGPU project.
One is..
to minify the export code as much as possible.
That export needs to be as seamless as possible.
And then if anyone else in this channel is interested, who wants to deploy something to the web?
I think a victory is if you get other people to actually use this.

**Wpmed** [00:20:12]
Yeah.
And then..
Yeah, I totally agree.
So like my goal would be if we can show that, hey, you can export stable diffusion to really complex model in like 10 lines of code or something like that.
I think that's really like a good selling point.
And once we have that, we can link these examples in the readme and link the compile scripts and stuff.
Yeah, so like..

**Geohot** [00:20:42]
Yeah, I mean, the more we could move out of extra, the more we can try to get upstreamed into main TinyGrad and make very clean and have an API that we're going to maintain for a long time, I think is important.
And then maybe after that, using all these abstractions to get TinyChat to work on that 1B model just in a browser.
I would also like to see not just export for WebGPU, but both WebGPU and Clang.
So like, yeah.

**Wpmed** [00:21:15]
Yeah, like WASM, right?

**Geohot** [00:21:16]
Yep.

**Wpmed** [00:21:18]
Like with Emscripten, yeah.
I think that's really doable.
Like you had that EfficientNet demo, right?

**Geohot** [00:21:26]
Yeah, yeah, yeah.
We have all the stuff.
We just kind of need to wire it up.
And then this LLM demo will work absolutely everywhere.

**Wpmed** [00:21:35]
Yeah.
Yeah, that's a bit different topic, but all this export stuff, like we have Metal, but we don't export Metal, but for iOS, I think some export model stuff could work, like exporting the Swift binding code, like the JavaScript binding code for WebGPU, and then you can just drag and drop the exported net.Metal or something into your iOS project, and you can just run it on the device.

**Geohot** [00:22:07]
Yeah, no, this seems like a great project for you.
And again, the success of this exporting project is judged twofold.
One, how short and simple, how maintainable is the API for us?
And then two, how many external people can we get to use it?

**Wpmed** [00:22:24]
Yeah.

**Geohot** [00:22:26]
Cool.

**Chenyu** [00:22:28]
Sounds good.
Okay, moving on to bounties.
I think ONNX is doing fine, I'm just learning all the weird things while reviewing those codes.
Oh, I add, I remove, I remove several exclude from the tests because now we support those.
The bitwise stuff and I think another one is if you do a power on the integer that we should also support.
I think it's doing fine.
We definitely.. 

**Geohot** [00:23:08]
Wait, do we support POW on integers in Tinygrad?

**Chenyu** [00:23:12]
Yeah?

**Geohot** [00:23:13]
How?

**Chenyu** [00:23:14]
Just round as if it's a float.

**Geohot** [00:23:17]
Oh, yeah, yeah, yeah.

**Chenyu** [00:23:19]
No, I think I agree with you.
POW should probably be an op.

**Geohot** [00:23:22]
I think POW should be an op and rewritten.
Yeah, well, I mean, because like POW is the.. There's like a math term for that.
Like what ADD becomes MUL, it's like MUL becomes POW.
Like operator..
yeah but it's called like it's called like operator weakening when you go from like i don't know maybe this is just like MUL to SHIFT or something but either way it's like ADD is to MUL is MUL is to POW uh and then..

**Chenyu** [00:23:50]
yeah you see you see that in the const's folding we fold the prod into like one so. 

**Geohot** [00:23:53]
Um and then like pow is to what's the what's the like hyper op of pow 

**Chenyu** [00:23:58]
I don't know it's like p versus np like np of np is still np

**Geohot** [00:24:02]
pow pow still pow?
What's pow pow?
You can imagine a reduce op pow, right?

**Chenyu** [00:24:08]
It's just pow.
It's just pow with bigger stuff.
I don't know.
Maybe.

**Geohot** [00:24:14]
Yeah, I don't know.
Yeah, that's a good thing, too.
We should get that stride folding merge, but we need pow for that, so I think that's a good project for you.
Proper int pow, not x2 log2.

**Chenyu** [00:24:07]
Yeah.
Okay, and I don't know if you have anything to add for ONNX, but I think it's moving fine.
It's starting to look a little bit complex for, maybe we can use more documents for like different modes for the pad and stuff like that.
But.. 

**Geohot** [00:24:48]
You mean, like documentation?

**Chenyu** [00:24:51]
So, you know, we support like six different modes for pad now.

**Geohot** [00:24:58]
I see.

**Chenyu** [00:24:51]
There's like const and there's like a reflect symmetry, a symmetry ceiling mode.

**Geohot** [00:25:01]
I mean, again, what we do all the time is like take the best of ONNX, Torch, JAX.

**Chenyu** [00:25:09]
Yeah.
I think those are definitely not more complicated than what it needs to be, but it can be better documented is my point.
Yeah.
So I think that's doing well.
I think direction is fine.
So we can move on to TensorCores.

**Ignaciosica** [00:25:26]
Hi.
Hello.
I've been working swizzling the store at the TensorCore, and I think I get it pretty right and clean.
I didn't make a PR yet, because it's kind of modified the views, the pushing the view right.
And I didn't want to add a work to Qazalin right now.
So once the lazy is merged, I may open the PR.
The thing is that it not only pushes the shape, but also if the shape is the same, it permutes.
Right now, it only..
which only reshapes the views.
But in order to swizzle the TensorCores, we need to also permute the shape.
So that's it.
And once we can swizzle the store, we can follow the documentation for the swizzles.
And I've been adding shapes for TensorFlow support for int8.
unsigned int8 and also yes now that if you can switch to the store it's pretty easy to add like all the TensorCores because it's straightforward you no longer have to guess the pattern and I.. 

**Geohot** [00:27:01]
Can you document this in a way I can understand that yeah

**Ignaciosica** [00:27:07]
Yeah, I was going to do so.
And I started thinking how to add the H100 WGMMA.
I think it's going to be a little bit different from the TensorCores.
It has some requirements for the inputs, but I'm going to work on that this next week.

**Geohot** [00:27:33]
Great, yeah, no, I would be super happy with, so, like, Flammit did a first pass at this, and I didn't really understand it, and then I refactored it into something that I didn't really understand, but was shorter.
It would be great to have something that we finally, like, understand, and I think we're getting there.
Like, I think we're getting there with this idea of, like, swizzles and pushing swizzles, and, like, this is what TensorCores actually are, as expressed in the UOP graph, and you can write, like, the closer we can get to writing what they are instead of what the transformation is, the better.
You see what I mean by that distinction?
We want to describe the computation and then TinyGrad figures it out.
Not we want to write in TinyGrad how to implement the transformation.
That's terrible.
So yeah, it's awesome if it's minimal.
Alright great.
Yeah, really exciting to see that.
We're going to get delete lazy merge this week.
Yeah.

**Chenyu** [00:28:31]
Great.
I added two more bounties for the symbolic chain stuff.

**Geohot** [00:28:39]
Is that person here, by the way?

**Chenyu** [00:28:40]
I don't see.
Oh, he's here.

**Geohot** [00:28:48]
Congratulations.
You're allowed to talk in the meeting if you want.
or you don't have to it's up to you.
You have to exit and rejoin if you want to talk to him.
I've been really liking those
symbolic improvement PR.

_HEADPHONE USERS PLS LOWER VOLUME!!!!!_

**Siedslykles** [00:29:15]
Hello.
Hello.
Hi.
Can you hear me?

**Geohot** [00:29:19]
Yeah, you got a bit of buzzing on your mic though, but I can hear you.

**Siedslykles** [00:29:24]
Okay, yeah.
The chain flattening and ordering is going pretty well.
It seems to have broken some of the Arange folding.
So I'm just trying to figure that out.
And then, yeah, I feel like it's pretty close.

**Chenyu** [00:29:41]
A lot of the bounties are also kind of fixing that, because Arange folding, the pattern for that is pretty rigid now.
And as we are moving these edge chains and the orders to be more flexible, those can improve as well.

**Siedslykles** [00:30:03]
So what do you mean by that?

**Geohot** [00:30:05]
So yeah, you can see how the Arange folding works.
The pattern is way more explicit than it needs to be.
There's many formulations of Arange that could be folded in the identical way, but the pattern matcher is too specific.
So ideally, part of the bounty would be making the Arange thing more generic to handle the new ad chain patterns.

**Siedslykles** [00:30:36]
Yeah, I don't know.
Like, one of the problems with when you flatten the whole chain is that there's a lot of patterns like x plus x, which should be folded to 2 times x. And then the problem when it's in a chain, you can have y plus x plus x, and that's not detected.
It's not the same as x plus x.

**Geohot** [00:31:05]
Yeah.
Yeah.
So that's part of it.
This is the challenge.
Yeah.

**Chenyu** [00:31:13]
I mean, so specifically for the two things you mentioned, if it's standalone, we have rules to fold loads.
But again, if now we are talking about a union over adds, what's the order we want to apply these so that it achieves the output you want?
It's the challenge of this reordering or flattening add chain.
I think if you make good arguments to change the orders for the top-wise stuff, that's probably fine.
I don't believe the current order that consts needs to be the last.

**Geohot** [00:31:49]
Oh, yeah.
No, no, no.
I mean, the whole reordering thing, that was only put in there to deal with these problems.
I don't really think it's not used anymore.
So that reordering used to be used in the linearizer, but it's not with the new linearizer.

**Siedslykles** [00:32:06]
Ah, okay.
Because part of the problem was, like, I just wrote my own order, because when you're in an ad chain, like, multiplication by constant is special, because you want those to end up next to each other.
But if I can change the order of.. Like, I was trying to change the order of all the ops.

**Chenyu** [00:32:34]
Yeah, so the bottom line is it's fine to change the orders as long as you have a good principle reasons to do so, and it doesn't cause regressions in other parts.

**Siedslykles** [00:32:48]
Yeah, OK.

**Chenyu** [00:32:52]
Yeah, because up to this point, those orders are kind of case by case set up.
We don't have a good way to think about that.

**Geohot** [00:33:00]
A principled way to think about it would be great.

**Siedslykles** [00:33:04]
Yeah, it's pretty fragile right now.

**Geohot** [00:33:07]
Agreed.

**Chenyu** [00:33:08]
Oh, that's why we want bounty on that right now.

**Geohot** [00:33:12]
Yeah, yeah, yeah.
That little thing where you can't apply some of the rules.
Cool.
Yeah.

**Chenyu** [00:33:29]
Good meetings this week.

**Geohot** [00:33:31]
Any quick questions?

**Chenyu** [00:33:36]
No, looks fine.

**Geohot** [00:33:38]
Okay, cool.
See you next week.
Thanks, everyone!
