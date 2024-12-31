# 2024-12-30 Meeting

## Highlights

- End of Year Rant [00:28:25](#end-of-2024-rant)
- CLOUD!!!!! [00:37:36](#cloud-news)

## Meeting Agenda

**Time:** 9:30 AM San Diego time (PST)
- No uop mutability
- Scheduler cleanups
- Merge am driver
- Bounties(x86, tensorcores)

## Audio

[Recording](https://drive.google.com/file/d/1Qw8wTkGJYS8F85R_Zvg9BuFJ_RnKx-Eo/view?usp=sharing)

## Chapters

*maybe gonna rethink chapters*

## Transcript

**Geohot** [00:00:01]  
Yeah, holiday meeting, holiday meeting, holiday meeting.  
So yeah, I guess Chenyu left us a list.  
So we'll go down to the list.  
We'll start with no UOP mutability.  
So right now we have UOP mutability.  
UOP mutability can't stay.  
So I have a PR passing test, but unfortunately it uses a weakset of all the tensors.  
So things like that can't stay.  
I merged this morning UOP children tracking.  
So now there's a property on UOPs called children.  
And it's a weakset.  
Well, it's a set, but it's effectively a weakset of all the living children of that UOP.  
And yeah, you can look in there to find children, which will eventually be rewritten instead of UOP mutability.  
So UOP mutability, it just ruins the beauty of UOPs.  
And the only thing you ever really need to change for a tensor when you realize a tensor, you don't actually want to change the UOPs themselves.  
You want to change where the tensor points.  
So yeah, what this does will allow us to...  
The tensor universe thing just doesn't work.  
The only graph that should exist anywhere in TinyGrad is the UOP graph.  
So the UOP graph sources are the parent nodes, and those are strong references to the parents because you can't construct a child without the parents, but you can construct... Children are not strong references because if a child has no other references to it, you don't want to keep it around, otherwise nothing will ever be cleaned up.  
So, yep, that's the rest of today and maybe tomorrow for me.  
But I hope to have UOP Mutability gone for the new year.  
And then it doesn't look like Gradient's going to get in this year.  
But I think that's the Cast Before View stuff.  
And, yeah, if you want to move on to that, Qazalin.  

**Qazalin** [00:02:11]  
Right.  
Cumulatively, since last week, we had a 42-line reduction in the scheduler.  
Around 30 if you also accumulate for the stuff I added with the tensor spec and the asserts.  
So overall just symbolic folding the manual stuff that we had for like checking is const is gone.  
It just uses the default stuff from ops.  
I also last night merged your view stuff for merging the views.  
I am gated by UOP mutability to be gone to merge the buffer having shape of size N because you cannot have one UOP become a new buffer.  
Then you would have two instances of the buffer and you would lose the underlying, like the device buffer and the dictionary.  
So that is gated, but hopefully that will solve your merge views.  
And literally, tensors can have a lazy data of buffer.  
It's a flat tensor and it doesn't have a shapetracker.  
The challenge I have come across is that if I give constants a shapetracker at the lower level, what happens is that lower has to also handle views.  
You see what I mean?  
Currently, uop.const on a lowerer has src of nothing.  
If I give it a src of view, it has to also merge views and do movement ops.  
It works, but does this break the abstraction of...  

**Geohot** [00:04:12]  
I'm fine with const not having a shape.  
I'm fine with const.  
If you try to call shapetracker on a const that doesn't have a view parent, it can just assert.  
I'm fine with that.  

**Qazalin** [00:04:27]  
I see.  

**Geohot** [00:04:28]  
Well, and the reason for that is because const exists in the final graph.  
Const continues to exist forever, even long after we've gotten rid of shapetrackers for things, whereas buffer doesn't.  
So I think buffer should have a shape, and I don't think const has to.  

**Qazalin** [00:04:48]  
Yeah, I think the only thing that would be so ugly is something in the scheduler that clears the sources.  
But I guess that's blind.  

**Geohot** [00:04:59]  
Something in the scheduler that creates the sources.  
I don't really understand.  

**Qazalin** [00:05:02]  
Clears the sources.  
Just makes the sources a tuple empty.  
That's what it has to do.  
Like, if you have a const 4-4, it becomes a const of nothing.  

**Geohot** [00:05:17]  
Yeah, I'll have to see this.  
But I'm OK with const and define var not having a space.  
They can if they have input views, or you can have like a view afterward, like you put a view on nothing and that's okay.  
That should always just be accepted as like a creating view.  

**Qazalin** [00:05:55]  
I'll work on cleaning up the shape stuff until we have, I'm very looking forward to the tracking rewrite, because I can finally delete the buffer.  

**Geohot** [00:06:06]  
You're talking about the graph rewrite map?  

**Qazalin** [00:06:09]  
Yeah, yeah.  

**Geohot** [00:06:10]  
So I ended up not needing that for UOP mutability.  
The key thing to realize about UOP mutability is many times, you have to be careful, but many times the rewrite map is equivalent to just linking all your nodes to a sink and then doing the rewrite on that sink and then looking at what ended up on that sink.  
That's certainly fine for Substitute.  
there's a lot that are more iffy, and I didn't work through all the cases.  
I just realized that in order to do UOP mutability, this doesn't matter.  
So, yeah, let's get no UOP mutability merged first.  
And then, do you know why we're still blocked on the gradient stuff?  
I haven't looked in a while.  

**Qazalin** [00:06:55]  
It does need cast before view, and for cast before view to really actually be a  
functioning thing in the scheduler, I need to get rid of the offer linking to tensor.  
So I just need some way.  
It doesn't have to be the tracking thing.  
Just some way that I can safely rewrite a UOP and still be able to backtrack to the tensor and realize that tensor, whatever it is.  

**Geohot** [00:07:23]  
I mean, you're welcome to, if you can use it, you're welcome to copy in my graph rewrite math stuff.  
It should work.  
Um, so yeah, no, I think, I think, okay, but that's, so is that blocked on you up mutability or not?  

**Qazalin** [00:07:38]  
Um, does the, if the map works, yeah, sure.  
I can base off of that then.  

**Geohot** [00:07:51]  
The map is only, the map is only three lines.  
Just pull it out of 8432, uh, and see if you can make it work for your purpose.  
Uh, I didn't merge it as a generic thing because yeah, I don't need it for UOP mutability.  
Um, but yeah, if you want to put it in the, uh, in the front of the scheduler, but yeah, I think, I think that's the, uh, the main thing for you to focus on, uh, getting the gradient stuff merged.  
Uh, so 80, if you can take over getting 8280 merged, uh, so 8280, uh, assert to prepare for grad UOP, I'll [link](https://github.com/tinygrad/tinygrad/pull/8280) it in TinyGrad dev is, uh, this, this needs to go in before, uh, we can merge gradient.  
And I think it's all scheduler things.  
Cool.  
Yeah.  
So if you can just work toward getting that in everything required to make that work.  
Yeah.  
Your mutability will be gone by 2025.  
And then hopefully gradient will be gone by first week of January.  
Yeah, that other gradient stack, I was writing all this stuff last night with trying to track parents and children of tensors.  
And I'm like, I'm never going to.  
I'm violating a core tenet of software development, which is do not put state in two places.  
State should be in one canonical place.  
And then if you want, you can build indexes on top of that state in order to quickly access it.  
But you should never be...  
Children is basically just an index on top of UOP cache.  
You could imagine iterating through the entire UOP cache and finding all the UOPs and then reconstructing the children graph each time, but that's really slow.  
So children is just an index on that.  
So yeah, indexes are fine, but state needs to live in one canonical place.  
And if you are going to have an index, you have to make sure it's perfectly in sync.  
So couldn't get rid of that.  
Yeah, I think it's only cast before view, blocking the gradient stuff.  

**Qazalin** [00:10:05]  
As long as I can get the bufferization going, cast before view will be pretty easy.  
So I'll look into that.  

**Geohot** [00:10:15]  
Cool.  
Yeah, I wrote tests for the map thing, too.  
Pretty.  
I mean, it's hard to come up with the cases that are hard.  
It's hard to think through independently of an application what they should be.  
So I think what the right approach is here is for you just to try to write the application, use that graph before map, and then if you can write a failing test case...  
If you can write a failing test case, you can put that on me and say, I expect graph before map, graph rewrite map to behave like X, it's actually behaving like Y. And then, yeah, I think that's a good way to go about it.  
But the obvious test cases I came up with, it works fine for.  
And it was hard for me to come up with without seeing the application.  
In fact, I went so far with that to realize that for UOP mutability, wait, I don't even need this.  
I can just do it with normal graph rewrite.  
So, yeah.  
Like always, always think about the application before you write generic infrastructure.  
Cool.  
Merge AM driver.  
Do we have the speed regression found yet?  
Are you there, Nimlgen?  
Going into some connectivity issues.  
Yeah, if you can hear me, I think that...  
Hopefully the speed regression's fixed, but even without the speed regression fixed, I'm okay with bumping the line count and merging it.  
I mean, look, I'm never thrilled about bumping the line count.  
There's three pieces of code that TinyGrad still relies on that are not in the TinyGrad repo.  
The first one is Python, and that one we're not going to do anything about because Python is, I think, some of the most beautiful code in the world.  
And the last two other pieces that TinyGrad uses are the kernel drivers.  
Think about anything you'd need that is external from just speaking directly to the hardware.  
Like imagine running this on a bare metal computer with no software at all.  
We need the drivers that are in the kernel to come into TinyGrad.  
And there's a few considerations that TinyGrad isn't dealing with right now.  
things like MMUs.  
So MMUs are physical things that exist inside of hardware.  
And that's a place where we can potentially always improve things by thinking through more clever ways to do that.  
But we can never improve it if all of that is being abstracted away from you by a driver.  
So that is why merging the AM driver is so important.  
And I think after this meeting, I'm going to bump the line count to 11,000.  
You know,  
New year, new lines.  
Can we have a negative line year in 2025?  
Can we end 2025 with less than 11,000 lines of code or even less than 10,000 lines of code?  
But yeah, I think I'll bump the line count.  
Let's get AM merged by the end of the year.  
The other place, so the drivers are one place where TinyGrad is still depending on dependencies.  
The other place where we're still depending on dependencies is for assembly compilers.  
So even with PTX, PTX is not really a... PTX is not machine code.  
You might want to call PTX an assembly language, but PTX looks a lot more like LLVMIR than machine code.  
So we are going to... in 2025 be adding our own assemblers.  
I think there's a decent start to the x86 assembler.  
I'm still waiting on benchmarks for that.  
I think tomsa, is that you with the x86 assembler?  
Yeah, you want to talk about it?  
If you exit and re-enter the chat, you can talk.  
But yeah, I think where we are to merge the AM driver is I'm going to bump the line count for merge AM driver.  
I will bump the line count to 11,000.  
The max 2025 line count. (hehehehhehehehhehehe)  
And let's get it merged by the end of the year.  
OK, x86 assembly backend.  

**Tomsa** [00:16:03]  
Can you hear me?  

**Geohot** [00:16:04]  
Yep.  

**Tomsa** [00:16:05]  
OK.  
I didn't really work on it this past week.  
I've been focusing on the  
the pattern matcher.  
But I wasn't here last meeting, but I heard the recording.  
And you talked about optimizations and vectorization.  
I guess vectorization shouldn't be done in the renderer.  
It should just translate to the IR.  
In the optimizations, there aren't really any.  
But I don't think it's super important, I guess.  

**Geohot** [00:16:37]  
Well, so I want to separate two concerns here.  
So there's one that, yeah, vectorization is an optimization and I don't think is a requirement for the bounty and I don't think is a requirement to get this merged.  
If all of the slowdowns are really due to vectorization, then that's fine.  
But...  
If the slowdowns are due to things like bad register allocation, we had some assembly backends back in the day, and the main problem with them is they would do stack spilling constantly.  
They would stack spill all these times you didn't need to.  
So how does this look with that?  
And that's why I want to see some benchmarks to compare it to Clang and LLVM.  
I expect this assembly backend to be consistently beating O0 with Clang.  
Not O2, but O0.  

**Tomsa** [00:17:29]  
I haven't done any benchmarks, but it runs more tests than Clang.  
For example, I was looking right now at the test transformer, and it does it in twice the speed as Clang.  
It's still a lot slower than LLVM, but... So there's no optimizations.  
There's no register coalescing.  
Everything has to move to registers.  
In x86, a lot of the instructions don't need...  all the operands to be registers.  
So if we took that into account, there would be a lot less register pressure and a lot less moves.  
But it doesn't do any of that because it's already 200 lines.  
And so I just went for the least amount of lines possible.  
But it's already faster than Clang, I'm pretty sure.  
But I could run some benchmarks.  

**Geohot** [00:18:13]  
I mean, faster than Clang at... So a lot of Clang slowness is not... I'm curious, actually.  
If it's faster than Clang's runtime, that's great.  
But a lot of Clang slowness is not at all due to the code Clang outputs.  
Clang is both very slow to run, and then Clang is also very slow to...  
The uuuvn has a fix for this.  
The ctypes.cdll is absurdly slow.  
So we're going to put in raw shellcode.  
Because eventually... So right now, x86 is still calling Clang.  
It's still calling Clang to do the assembly.  
And we're going to need to remove that.  
Not for the bounty.  
But... Yeah, actually... That stuff's going to go away.  
Yeah.  
Yeah, so the x86 device, you're not going to be able to use the Clang compiler like that anymore.  
Maybe it's fine.  
I don't know.  
We can deal with that later.  
But yeah, just give me some benchmarks for various stuff.  
But I think we're pretty close with that.  
And then that bounty will be yours.  
Also, there's other like, so you have things like move to reg R15.  
Why?  

**Tomsa** [00:19:46]  
Because only general registers can take immediate values, so float registers can't.  
So you can't move a floating point value to a floating point register.  
You need to use a general register.  
So I use that, and then I  
I mean, that...  

**Geohot** [00:20:04]  
That's not exactly what I'm saying.  
What I'm saying is that should be dealt with as a rewrite rule, not as... Like, why does that have to go in R15 specifically?  

**Tomsa** [00:20:18]  
That's just the designated temporary register.  
Because there's other instructions that need R15.  
For example, div.  
And there isn't... I don't think there's a way to...  
Do it in rewrites.  
DIV requires a temporary register.  
There's also float compares require a NaN check, which requires an additional register.  
I don't think there's a way to rewrite that.  

**Geohot** [00:20:43]  
Why not?  
We have to basically, like, this should be a rewrite rule.  

**Tomsa** [00:20:55]  
I don't see how.  
I guess I can think about it.  

**Geohot** [00:20:57]  
Well,  
The way I kind of imagine it is, and I'm not sure all of this needs to be done for the bounty.  
I think the only real requirement for the bounty is it isn't egregiously slower than Clang O0.  
And I mean the generated code.  
But the register, so you have register assignment, right?  
You're mapping each UOP to a register.  
And we want that to be a one-to-one mapping.  
We want each UOP to live in a register, and this is going to move into some stuff that we don't quite have the infrastructure for yet, which is UOPs that are, like, for example, if an assembly language has something that can add three things together, if there's an instruction that can add A, B, and C together all at once,  
we could make a rewrite rule that's kind of called ops.instruction.  
And then ops.instruction is a rewrite rule where it takes in the two adds and converts it directly to that instruction.  
Or you can think of things like a lot of load instructions will do indexing in the load instruction.  
So that's eventually where these things need to go.  
And then we want a register.  
I think it's called register coloring.  
Use a graph coloring algorithm.  
And that graph coloring algorithm should operate on the UOP graph to assign each UOP to a register.  
Let me see how this works now.  
So yeah, the registers are assigned at...  
Ideally, you even want the registers to be assigned, I guess you can't do it before linearization.  
Maybe you can, and maybe that can affect linearization.  
There's just a lot of complexities here that we haven't fully ironed out exactly where things belong.  
But certainly we want each UOP to correspond to a single register and not have a designated temporary register.  
But again, I'm not sure it's a prereq for the bounty.  
We'll just gate that on benchmarks not being worse than Clang O0.  
Sound good?  
Tensor Cores got merged, if you want to talk about that.  

**Ignaciosica** [00:23:41]  
Hi, hello.  
Yes, Tensor Cores refactor finally got merged.  
Now all the swizzle that is performed for the TensorFlow course is according to the documentation for all the backends.  
And now, before taking up the open bounties,  
I have locked.  
I am working on refactoring ops_python to see if I can simplify it a little bit more before adding new tensor cores.  
Because for each tensor core that needs a swizzle, I actually have to add a new option in ops_python for that specific swizzle.  
So I'm going to see if I can simplify, or at least  
Make it more convenient.  

**Geohot** [00:24:32]  
So I want to say one thing about ops_python.  
I really like the idea that ops_python has a different implementation than the implementation in Tensor Core.  
Like ops_python should be explicit, slowest, most feed forward way of doing the Tensor Core.  
compared to the tensor core class, which is used to optimize the graphs.  
So the thing that I don't want to see about a refactor here is basically like taking ops_python and having ops_python rely on things like the swizzle from the Tensor Cores.  
If it relies on obvious things like the dimensions, I think this is fine.  
But yeah, it can't rely on the swizzle itself.  
The swizzle itself should be written in an explicit form instead of a transformation form.  
And then that explicit form is the test against the transformation form.  
Because if it's the same thing, what are you really testing, right?  
So yeah, just something to be careful with that refactor.  

**Ignaciosica** [00:25:35]  
Yes, I agree with that.  
I was thinking about taking, like you said, the simple input, like the dimensions or the elements per thread.  
And the refactor was more like moving the logic, staying with the same logic there is now, like no changes in the implementation, but rather where they reside, like getting the element from the A matrix or the B or C. But I don't know.  
I'm going to work on that.  
And if it's good, I'm going to make a PR.  
Also, I am just going to add a new TensorCore.  
But thanks for the feedback.  

**Geohot** [00:26:14]  
Cool.  
Yeah, no, I think you've really been going above and beyond with these refactors.  
So I think we can all increase the TensorCore support bounties to, let's say,  
say, $400 each on account of the beauty of the code.  

**Ignaciosica** [00:26:44]  
OK, thank you.  
And to mention only for the H100 Tensor Cores, if it wasn't for the special requirements that it has for the B matrix to live in shared memory, it would work.  
But this will require an adaptation for that.  
And from what I'm looking, it's a little bit .. Do you remember the special registers we talked for AMX?  

**Geohot** [00:27:23]  
Yeah, yeah, yeah.  
It seems kind of like the AMX thing.  
Yes.  

**Ignaciosica** [00:27:29]  
I'm going to work on that, but maybe it's going to need a little bit more than only defining the sensor curve like we thought before.  

**Geohot** [00:27:41]  
Yeah, that makes sense.  
Cool.  
Yeah, no, I mean, that is why they're different bounties, and we're going to have to figure out what the H100 needs to start making these things fast.  
Yeah, 2025 is going to be all about speed.  
I see the add mod to tensor require, like, some test is failing.  
We should figure out why that test is failing and fix that and not just add a contiguous.  
But yeah, these are in Chenyu's wheelhouse.  
Yeah, cool.  

##### End of 2024 rant  

That's a good holiday meeting.  
Great things planned for 2025.  
2025, I think we'll see the first truly complete stack.  
Well, I think we'll get them for CPUs first.  
Because CPUs don't really have a driver.  
But maybe when we get... Maybe it'll be RDNA 3.  
If we get TinyGrad to output RDNA 3 machine code, RDNA 3 machine code combined with the AM driver is the entire game.  
There is no more external dependencies anywhere.  
And that's all kind of step one to building a complete sovereign stack for machine learning.  
And the reason that you need to build this stack, this isn't just some academic exercise.  
If you don't build this stack, you're going to be dependent on NVIDIA for the rest of your life.  


NVIDIA's moat is not CUDA.  
People think NVIDIA's moat is CUDA.  
This just isn't true at all.  
NVIDIA's moat is an ecosystem.  
People mistakenly call this ecosystem CUDA, but it's not CUDA.  
CUDA itself is a very mediocre language that really is... I think Intel's even got a better strategy with trying to make OpenCL good.  
NVIDIA just made CUDA for...  
Probably because OpenCL spec was insufficient or something.  
And they just didn't feel like modding it.  
And they're just like, whatever, we'll make our own language.  
We can go back.  
I remember playing with CUDA in 2008.  
CUDA goes way back.  
So their moat is not CUDA.  
Their moat is an ecosystem.  
And this ecosystem is a spidering web of dependencies.  
You have PyTorch, and PyTorch depends on Triton.  
And Triton depends on, well, CUDA, but also Cutlass and CUDNN.  
And maybe Triton doesn't depend on CUDNN, but Torch can depend on CUDNN.  
And then, of course, you want multi-device stuff.  
You're going to need Nickel.  
And then all of this stuff speaks to this NVIDIA driver, which you think is open source, but isn't really open source because there's a 50 MB thing called a GSP, right?  
The graphics subsystem processor, which is the driver, is just basically a shim on top of that, which is true for AMD, but not true for Intel.  
Sorry, which is true for NVIDIA, but not true for AMD.  


AMD's driver is pretty close to the metal.  
I've looked into AMD's firmware and there's not much there.  
Like you're almost at the raw hardware.  
And then once you're at the raw hardware, imagine 11,000 lines of Python that is capable of directly driving the hardware.  
You're going to need to write all of this when you build your own hardware.  
If you want to succeed at building your own hardware, that's the easy part.  
You want to make a chip?  
Easy.  
You want to make an ecosystem that makes modern ML software work with that chip?  
That's next to impossible.  
And that's what every single company has failed at.  
The only companies that have succeeded at this are companies that write their own frameworks.  
PyTorch succeeds at this because, well, they're basically like it's NVIDIA's framework.  
Google succeeds with the TPU because they've written TensorFlow and JAX.  
They've written frameworks.  
When you look at companies like Grok and Cerebus, even TensTorrent, they don't succeed because they haven't written widely adopted frameworks.  
Apple's trying this.  
Apple understands this strategy, and this is why they're going ahead with MLX.  
In order to get your, and with MLX, it's even easier because the Apple GPU is not that radically different from an NVIDIA GPU.  
But once you get out to these weird, this weird hardware, like Cerebus and Grok don't have DRAM.  
Um, you need, and TensTorrent is TensTorrent is weird in all sorts of ways too.  
You need your own sovereign framework to, to write it.  


So it's going to be a very long journey.  
It's going to take us many, many, many years, but our first step is not building a chip.  
Do not judge tiny corp success based on whether we have taped out a physical chip.  
This is a cost.  
Taping out the chip is a cost.  
Companies are judged, I think, Etched to some of the biggest clowns in the industry.  
They can't wait to tape out a chip that has transformers.  
What are you doing?  
Do not judge us based on whether we've taped out a chip.  
Judge us based on how good our framework is.  
Not just on NVIDIA and not just on AMD.  
but on all of them.  
If we write stuff correctly, we can make progress generically in lockstep across all of the hardware, across AMD, across Nvidia, across Intel, across Apple.  
Those things are all GPUs.  


Once you get into the realm of things that are not GPUs, we aren't explicitly targeting them yet.  
Probably our first non-GPU target  
Well, I guess CPUs.  
CPUs are even easier than GPUs.  
But our first non-GPU target will be the Qualcomm DSP.  
I got an email from some startup offering $5,000 for a bounty to get the Qualcomm DSP to outperform SNPE, or be equivalent in performance to SNPE on MobileNet.  
So if someone's interested in that bounty, I told them to come post in our Discord.  
I said, for $5,000, it's probably not worth changing the company's priorities.  
But yeah, the Qualcomm DSP and hardware that looks like that will probably be our first target away from GPUs.  
And if you look at Qualcomm's new DSPs, they have something called...  
They have a matrix unit.  
I mean, they have a vector unit on the old ESP.  
They have these very wide vector words.  
But they have a matrix unit on the new ones.  
And the matrix unit on the new ones, while it's not a systolic array, the whole architecture of the thing looks very similar to Google TPU.  
So there's things that look like the Qualcomm DSP and the Google TPU that I think are probably going to be the next type of architecture support for TinyGrad.  
But as you get into these sort of architectures, it becomes even more important that you're outputting the assembly yourself.  
You can't, for a CPU, you can basically give a CPU any dogshit C code, put it into a modern compiler stack, and it does an okay job.  
It's not a phenomenal job, but it does an okay job.  
You're going to get 50% of the performance of the CPU.  
You know, if you want to get 100, you can hand to it.  
Maybe you'll even get 20.  
But with things like the DSP,  
If you put it into a normal C compiler stack, if you write the code in a normal way and put it into a C compiler stack, you get 1% of the performance.  
And that's why it's so important that we actually output the assembly ourselves.  
And then even the DSP, there's things that are even harder than that.  
So once you get to the Google TPU, you're looking at VLIW instruction words where the chip probably doesn't even have things that handle, for example, pipeline stalls.  
You have to be reasoning about pipeline stalls in your compiler.  
which something I got wrong early on about AI kind of compute, the VLIW stuff is coming back.  
VLIW is totally fine for static workloads.  
And by static workloads, I mean workloads that don't rely on loads and stores, or even worse, comparison branches,  
that aren't predetermined at runtime, predetermined at basically compile time.  
Early runtime is okay too.  
Like when we have things like the variables that can adjust the length of the loop, that stuff is determined, but it's determined before any of the code runs.  
And that's the key thing, right?  
You don't have like, I don't know, you can probably come up with some type theory way to describe this, but hopefully you kind of see what I'm talking about.  
Maybe the simplest way to talk about it will be UOP graphs.  

**Geohot** [00:36:39]  
Okay, any questions?  

**Geohot** [00:36:47]  
Yeah, the RDNA3, RDNA3, I want to also get to like, I want to have a beautiful, some beautiful code in TinyGrad, and this will go into our 11,000 lines, that actually is the machine code for these systems.  
So like the thing that we should be outputting is not move R1, R2, but rather the four byte machine code that corresponds to that.  
And we can go directly from the UOPs to that machine code, concatenate the strings together, shove it in GPU memory.  
And then, yeah, it's a completely self-contained stack for machine learning.  
Yeah.  
You're going to need to do this for your hardware anyway.  
And if you can't do it on AMD's hardware, oh, I guess I'll talk about one more thing.  

##### CLOUD NEWS  
2025 is going to be the year of the TinyGrad Cloud.  
We currently have people in the factory building nine TinyBox reds for the cloud.  
And we're going to, these cloud machines are going to be beautiful.  
They're not even going to have, they're not going to have an operating system on them.  
We're just going to pixie boot them into a very minimal Linux, Python, TinyGrad environment that runs the cloud backend, and then runs the cloud backend, the AM driver, and the, some very basic way, probably even through TinyGrad to access the disks  
And then we have some gateway server, which does graph rewrites to distribute them to our cloud correctly.  
But it's a full networked TinyGrad ecosystem.  
So we can start to think about how to, probably not next MLPerf, but the MLPerf after.  
I want to see all 54 of the GPUs working together, communicating over the Ethernet or the InfiniBand or whatever.  
And yeah.  
So to everyone in here, probably in two months,  
We're going to give people beta access to the cloud.  
I think it's too early to do anything for that yet, but we'll have a cloud access channel.  
We'll give people access keys and it'll be free.  
It'll be free for probably this whole year to everybody who's working with TinyGrad.  
I mean, you can only use the cloud with TinyGrad.  
So yeah, if you want free compute, use TinyGrad, use our cloud.  
And yeah, it'll be fun.  
Are you guys making a nice user API for renting hardware yourselves?  
We're going to run the data center.  
We're not, this is not some vast AI hyperbolic style thing where you can add your own GPUs to the cloud.  
You know, everyone loves decentralized stuff, but it's usually their own call engineering wise.  
So no, this is not a decentralized cloud.  
This is a normal cloudy cloud built on open source software that we're going to run.  
And if the people who are using it, if it starts to basically get adoption, we'll have the free version.  
We'll expand the free version out to some amount of machines.  
And then if there's demand for more machines, well, we'll have a paid version that we operate at a profit.  
And yeah, I think we can be competitive with all of the big clouds too through basically... Our number one trick is using consumer GPUs.  
Yeah, we're going to use...  
especially AMD consumer GPUs.  
If you can use AMD consumer GPUs and you manage to make this stable and a good experience for people, there's a massive arbitrage opportunity over H100s.  
So, yeah.  
Yeah, cloud in 2025.  
Yeah, I think you'll be hearing more about that as it gets closer.  
I'll post some nice pictures.  
Putting nine machines.  
We're not even putting them in a rack.  
Racks are too expensive.  
We've got to buy rails.  
It's expensive.  
We're going to put them on shelves.  
We're going to buy cheap metal shelves from Uline.  
Stack the computers on some Uline shelves.  
Plug them into each other.  
And that's a cloud.  
All right.  
Happy New Year.  
Happy Holidays.  
Merry Christmas.  
Happy Hanukkah.  
This is going to be a great year for TinyGrad.  
See you all later.  
