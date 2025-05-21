# 2024-12-16 Meeting

### Weekly nugget of wisdom from tinycorp meeting

_around [00:16:56]_  
Software engineering is not about writing code.  
Software engineering is about communication.  
My operating systems professor told me this.  
He's like, George, the point of code is not for a computer.  
The point of code is for a human to read it.  
For the computer, give it machine code.  
But the point of code is to be readable and understandable and make the idea more readable and more understandable.  

### Meeting Agenda

**Time:** 9:30 AM San Diego time (PST)
- Company update
- Drivers, AM and QCOM, openpilot tinygrad runner
- Big graph cleanups
- New gradient API
- Tensor is UOp? effect of scope, mutation, realize
- Ops.POW, stable sigmoid, view reshape
- Webgpu
- Line crisis, chinese gpu, improve speed
- Bounties: onnx, tensor cores, fast gemm, matcher speed, OSX GPUOcelot, int64 indexing

### Audio

[Recording](https://drive.google.com/file/d/1yeXdjUUJYyJvP254cvjg09n_zqNR6qh8/view?usp=sharing)

### Chapters

- **00:00:00 Company Update**  
  Tiny Box Pros are shipping this week.

- **00:00:28 Drivers: AM and QCOM**  
  Discussion on QCOM driver timeout issues

- **00:10:38 Big Graph Cleanups**  
  Deletion of Lazy buffer is complete! Next steps focus on buffer scope, mutability, and documentation clarity.

- **00:16:50 Tinygrad Improvement Plans (TIP)**  
  Establishing TIPs for improvements. Emphasis on documentation before implementation.

- **00:27:30 New Gradient API**  
  New gradient handling with higher-order derivatives. Removing `no_grad` and improving clarity.

- **00:32:33 Stability Improvements for Ops and Sigmoid**  
  Rewrite rules for stability in numerical operations like sigmoid and hyperbolic functions.

- **00:38:14 Midterm Focus: Speed, GPUs, and Lines**  
  Addressing Python overhead, kernel inefficiencies, and exploring new GPUs (e.g., Chinese GPUs, USB GPUs).

- **00:43:05 Open Bounties**  
  - **ONNX Top 100 Models**: Bounty increased to $400 for testing and supporting top 100 ONNX models.  
  - **TensorCores**: Progress update on TensorCore optimizations and testing.  
  - **Fast GEMM**: Plans for speed improvements via double/triple buffering.  
  - **Matcher Speed**: $2,500 bounty for 8x speed improvements.  
  - **WebGPU**: $1,000 bounty for running TinyGrad in-browser via WebGPU.  

- **00:52:07 Int64 Indexing Fixes**  
  Updates on PRs for Int64 indexing. Testing edge cases for correctness.

### Transcript

**Geohot** [00:00:03]
Ok uh,
Company update.
We're shipping Tiny Box Pros this week, probably.
We're getting the last parts in.
Got them all on a table.
The whole Mars catalog tweeted about it.
That's pretty good.
Getting a whole lot of those built.
That's the main company thing.

**Chenyu** [00:00:28]
Okay, this week we start with drivers, so both for AM and QCOM for Nimlgen.

**Nimlgen** [00:00:44]
Yeah, so for the [QCOM problem](https://github.com/tinygrad/tinygrad/issues/8242), I'm not really sure how they reach this timeout of 30 seconds.
That was definitely, like, the way it works for QCOM, we just completely wait for, like, for the signal.
We just go and sleep, waiting for the signal.
And the previous problem was, like, we can wake up after they sleep.
After that, we just check timer and exit.

**Geohot** [00:01:22]
It did eventually get the signal, right?
That's why the two numbers were the same?

**Nimlgen** [00:01:26]
Yeah, but it was bigger than 30 seconds.

**Geohot** [00:01:31]
Well, I don't think it was bigger than 30 seconds, right?
Because you don't actually check it.
You have to sleep after the if, right?

**Nimlgen** [00:01:35]
No, no, no.
I mean, it's just in the while loop, so...

**Geohot** [00:01:43]
It's fixed.
You fixed it now, but I think the last one didn't actually trigger.
But regardless, those sleeps are getting very big.
I don't think there's any advantage to that, right?
Like, why should that ever sleep for more than like 100 milliseconds?

**Nimlgen** [00:01:59]
Yeah, so for AMD that work this way.
Because actually in QCOM driver you cannot provide timeout, I think.
Or maybe you can.

**Geohot** [00:02:09]
No, no, no.
What I'm saying is you have that loop and that sleep thing is actually just like a CPU sleep, right?
Your CPU is sleeping for seconds.
Why?

**Nimlgen** [00:02:21]
Yeah, so waiting for a signal, I mean.

**Geohot** [00:02:24]
No, I know, but in that loop, you have the sleep.
How long can that sleep be?
How long does the CPU... How often do you pull, basically?

**Nimlgen** [00:02:36]
So, for... Yeah, I mean, for QCOM, there is no timeout for this syscall.
I mean, I need to double-check that, but currently, yeah, there is no timeout for syscall, so it can go and sleep forever.

**Geohot** [00:02:55]
What's actually implemented in underscore sleep?

**Nimlgen** [00:03:01]
So, basically, a call to a driver, like, go and wait for a signal, yeah.

**Geohot** [00:03:09]
Oh, so it's not even using time spent.

**Nimlgen** [00:03:13]
Yeah, I mean, time spent is actually for AMD.
That's actually just go to sleep after two seconds.
So just to be really fast during BEAM.
But for QCOM, this is disabled because I think we want to sleep.

**Geohot** [00:03:28]
Yeah, but so it did eventually get the signal, right?
Because that's why the two numbers are the same.

**Nimlgen** [00:03:33]
But actually, yeah, it took longer than 30 seconds.

**Geohot** [00:03:42]
Well...
It took longer than 30 seconds.
No, I don't think so.
I'm reading the old code here.
We don't even... I don't even know.
Like, the old code had the value check before the sleep.

**Nimlgen** [00:04:10]
Yeah.
So, that's basically...
Yeah, so basically that's like the fast path.
You can just have already valid value and you should not go to sleep.

**Geohot** [00:04:19]
Where are you even getting 30 seconds from?
Where is this 30 seconds?

**Nimlgen** [00:04:27]
So I'm saying that it's been waiting longer for than 30 seconds because it actually happened.
Like the timeout happened.
Like the while loop checks as a timer.

**Geohot** [00:04:41]
How tightly does that loop spin?
How often does sleep just... No, for Qcom, it's just one sleep.

**Nimlgen** [00:04:50]
It's just not loop at all.

**Geohot** [00:04:53]
Well, yeah, well, then there's just a bug in this code, right?
Because you have the while loop, then you have a check, then you have the sleep.
Unless I'm reading this diff wrong.

**Nimlgen** [00:04:58]
Yeah.

**Geohot** [00:05:11]
I don't even understand how this ever worked, right?
Because, like, you have the while loop.
Then you check the condition, which might exit really quickly.
Then you sleep.
But then you raise the error no matter what happens next.
Oh, no, I see.
Okay, no, no, no, I see.
So that while condition will actually trigger and it'll do the sleep.
It'll enter the loop again and then check the value.

**Chenyu** [00:05:38]
Okay let's follow up this separately uh we will we are also asking comma if they have a reliable reproduce of this or at least a way for us to trigger and know we have fixed the issue that will happen regardless

**Nimlgen** [00:06:05]
I mean, no.
I mean, I fixed some logic, I think, mistake in this while loop, but definitely they had some behavior, and that's the reason why they spent 30 seconds in the syscall.

**Chenyu** [00:06:20]
Yeah, I mean, I understand when you say you fixed it, it seems like you fixed something.
I think we just need better testing around this as well.
It's like, so what happened was OpenPilot merged their new TinyGrad runner that used the very recent TinyGrad, but they need to revert it because on the real device, something bad happened.
But this passed our CI and their CI, and still bad things happen.

**Geohot** [00:06:51]
Yeah, I wonder if there's some conflict because they're actually using the GPU.
I wonder if that's the issue.
Is there any way we can fuzz that while things are running?

**Nimlgen** [00:07:04]
I think ideally maybe we need their setup somewhere.

**Chenyu** [00:07:08]
Yeah, we need some way to reproduce this.
Yeah, we cannot fuzz.
Ideally, yes, but we start with something that's really bad and we fuzz from there.

**Geohot** [00:07:20]
Well, I mean, yeah, the problem is their setup is... You almost want just something that just uses the GPU in all sorts of weird ways.

**Chenyu** [00:07:28]
Yeah, I mean, at least what we can do is bring one of the comma runner and just run whatever on it for hours, right?

**Geohot** [00:07:39]
Yeah.
No, I mean, they can also do that.

**Chenyu** [00:07:41]
Yeah.
So something for that to start with, we want to reliably.
This is definitely important.
We want to fix it.
We cannot be the one who blame other people's driver are bad and our driver also crash.
Okay.
How about AM?

**Nimlgen** [00:07:57]
So yeah, for AM, I still have a speed to match the AMD driver, and also there is one weird behavior when accessing memory just sometimes return like all Fs.
So yeah, and that's pretty strange because I have...
Well, like, their kernel driver, like, modified would, like, remove... So, basically, it's the same logic as our drivers, and it works.
So, I think I'm just doing something wrong on the CPU side, maybe.
I know.
Yeah, I'll double-check that.
So, yeah.

**Geohot** [00:08:41]
In general, when I see stuff like you're reading RAM and it's giving you all Fs, it's some, like, cache coherency issue?
Like, it's somehow in the cache stale as all Fs?

**Nimlgen** [00:08:52]
Yeah, or maybe, I don't know.
I mean, I'm reading, like, the GPU mapped thing.
I'm just reading VRAM.

**Geohot** [00:09:03]
Is it cached or no?
You think it's not cached?

**Nimlgen** [00:09:06]
No, I think it's not cached.

**Geohot** [00:09:10]
Because, you know, there's two ways to do that, like over PCIe.
Some PCIe stuff can be cached.

**Nimlgen** [00:09:18]
Yeah, I mean, I need to check that.
But no, I think it's not cached.

**Geohot** [00:09:26]
Okay, sounds like we have a good path there.

**Chenyu** [00:09:28]
How slow is it?
And is it like consistently slow or just slow at some part?

**Nimlgen** [00:09:35]
No, yeah, it's slow, like the step time is slower as well.
So just several milliseconds, and in total it's just several, like seven or ten minutes, but yeah, I'll find this.

**Geohot** [00:09:49]
I think the question is more, like, is it just, is it evenly distributed across all the kernels slower, or is it just like a few kernels that are slower?

**Nimlgen** [00:10:00]
Um...

**Geohot** [00:10:06]
Like, maybe all kernels that use shared memory are slower or something.

**Nimlgen** [00:10:09]
Yeah, that's a good thing to know.
I've just noticed that one kernel, which is, like, reproducible slower, is just using tensor cores, so maybe it's, yeah.

**Geohot** [00:10:20]
Yeah, I mean, there's also, like, so much there of the speed also comes down to, like, if your beam isn't hitting the... Oh, I guess, no, you cache the beam.
Do you cache the beam on... 

**Nimlgen** [00:10:27]
Yeah, yeah, so it's running the same beam.

**Geohot** [00:10:31]
It's running the same beam, yeah.

**Chenyu** [00:10:34]
Sounds like a good progress.

**Nimlgen** [00:10:38]
So yeah, and for...
For [the viz](https://github.com/tinygrad/tinygrad/pull/8211), I mean, it's like almost ready from the perspective of the profiler refactor.
The only thing to solve is from the viz side.
Like, I think we just want to support... So currently, you cannot launch both profiler and viz equal one.
so that's for me to fix and um actually yeah i mean that's uh quite tricky i think to fix so like we currently launch viz so using at exit function so i do the same for the profiler but
And because of that, yeah, I mean, we need to somehow order them.
Just, I don't know.
I don't know if it's a good idea to access, like, my profiler stuff and devices from the ops.py.
Or, like, access... Yeah, it's just...

**Geohot** [00:11:46]
Yeah, I think what we want to do is we want the profiler to be universal and not just for HCQ devices.
So I'm okay with moving the profiler to ops.py and then the device can implement a profiler kind of.
Because I want this profiler to work for Metal, to work for OpenCL, to work for everything and just get the basics of all the stuff, even if it's not perfect.
So yeah, no, I think that the profiler is very fundamental.
And yeah, I think that eventually I want this profiler to work for everything, and it should be an integral part of Viz.

**Nimlgen** [00:12:24]
OK, yeah.
So also for UI, I'm still using Perfetto.
I don't know if we want to rewrite this with something, but... Yeah, actually, the one thing I really hate about Perfetto is just showing these dependencies, because it's just really strange to show these arrows between blocks, because you need... You cannot just...
Like, say, two IDs of the blocks, you need to just... To draw an arrow between two blocks, you need to use timestamps.
So, I don't know.
And I've seen some weird behavior because of that.
Because if some blocks have the same timestamp, it's just not really logical.

**Geohot** [00:13:17]
We probably want to eventually... I mean, my thought would be to use the same... Maybe...
Qazalin has more thoughts on this.
I want to use the same graph layout engine would kind of be my idea.
And then you can kind of like lay the, you lay out every node in the graph based on its size.
And then you link them with the graph nodes.
I think that'd kind of be a cool way to do it.

**Nimlgen** [00:13:44]
Yeah, maybe.
Also, it'd be interesting to see at performance.
Okay, I'll try this.

**Geohot** [00:13:51]
I don't know if you have to.
If you can just use Perfetto, it's fine for now.
We can always change that later.
That's not a big deal.

**Nimlgen** [00:14:00]
Yeah, okay.

**Chenyu** [00:14:15]
Cool.
Okay.
Let's move on to BigGraph clean ups.

**Qazalin** [00:14:25]
Yeah, so we merged Delete Lazy.

**Chenyu and Geohot** [00:14:30]
Great, yeah.

**Qazalin** [00:14:33]
Lazy's gone.
I'm so happy.
And yeah, we've got a lot of cleanups to do now that there's no Lazy.
I think there are [two fundamental questions we haven't answered](https://github.com/tinygrad/tinygrad/issues/8273).
There's the const thing, then there's the
mutability issues, and the overall... 

**Geohot** [00:15:14]
Well, I think that they both boil down to, and if you saw my [abstractions4](https://github.com/tinygrad/tinygrad/pull/8272/files), I think we rushed into this way too much, and I think as a challenge for you this week, I don't want you to write any code.
I just want you to write docs exploring multiple different ways of doing this, and write the docs to be so clear, such that I'll write the code, but it should be so easy once I see the doc.
Because we're maintaining way too much complexity just in the code, and I think we're wasting tons of time trying to actually implement these things when we haven't thought through all the implications of it.
There's two basic questions.
that I think are like really fundamental and how we answer them, answer everything else.
One is what tensors should get buffers, right?
So all the tensors you explicitly realize definitely need to get buffers, but should any others?
And then the other question is what should the scope policy of buffers be?
When do you free a buffer?
And those, until you have very clear answers to those two questions, I think it's hard to talk about anything else.
But, you know, I mean, I'm working on docs for that for all of these things.
You can think about what the eventual like tinygrad governance is going to look like.
And we're going to move to something that look a lot like [PEPs](https://peps.python.org/pep-0468/).
All right.
You have a TIP, a Tinygrad Improvement Plan.
And, you know, you write it up such that you have an abstract, you have the motivation,
you have the specification and you have concerns and alternatives.
So, yeah, no, instead of doing big minus 500 lines PRs, let's write docs.

**Qazalin** [00:16:50]
It's a good diff, though.
Yeah.
It's showing, like, what's possible.
All of test tiny passes.

**Geohot** [00:16:56]
No, no, no, no, no, no.
Listen to me.
It's not a good diff because I can't read it, right?
Software engineering is not about writing code.
Software engineering is about communication.
My operating systems professor told me this.
He's like, George, the point of code is not for a computer.
The point of code is for a human to read it.
For the computer, give it machine code.
But the point of code is to be readable and understandable and make the idea more readable and more understandable.
So when you give me that PR, I can't read it.
Um, so yeah, no, like focus on, on, on, and I think that the, the, the big graph project itself would have went a lot better if we'd done it like this, where it's just like, okay, what exactly do we want to change here?
What is the current behavior?
Half of it is just figuring out what the current behavior is.
And then the second half is figuring out, okay, what should the new behavior be?
What are the changes?
Then it can be like, like addressed in a more principled way.
But, yeah, no, I mean, again, and, you know, we've had this conversation before.
It's really if you write code and you're the only one who uses and understands that code, it's not good code.
It doesn't matter what it does.
That's completely irrelevant.
It's all about communicating.
No, and I know I know sometime I sometime I shortcut this.
Sometimes this is maybe on me, you know, not not going through the explicit process externally that I go through in my head.
But I do go through that process.
I go through a process of... I'll only write it down if the complexity is really more than I can manage in my head.
But I hope that my stuff is readable to everybody here.
And if it's not readable or something doesn't make sense, call me out on it.
It's my job to fix it.
If I've written...
If the new linearizer I wrote doesn't make any sense to people, then it's on me to fix it.
I'm not saying it has to, look, it doesn't have to make sense for every single person in the world.
You're never going to get that.
But to other people who are working on this code base, it should be very understandable.
Or otherwise, it's still got to be worked on.
So Tinygrad Improvement Plans (TIP).
What's the first one?

**Qazalin** [00:19:38]
Const.

**Chenyu** [00:19:39]
Let's do the const and those buffer and views and buffer views.

**Geohot** [00:19:50]
Yeah, so maybe the other thing, why does view sometimes have two sources and sometimes have one source?

**Qazalin** [00:19:39]
That carries from the lazy days.
Before delete lazy, the scheduler didn't control the actual buffer.
So I need a way to give every single operation a buffer, a UOP buffer.
So every parent has a buffer because lazy buffer has a buffer on it.
It created on init.

**Chenyu** [00:20:07]
Yeah.
So I would say this is what exactly we want to be put into a docs like this.

**Qazalin** [00:20:13]
Exactly.

**Chenyu** [00:20:14]
You describe a problem and this is your solution.
I'm pretty sure you have think through like many different ways to implement this.
But as a, say for me, I was reading this code yesterday and I saw there was like a schedule function.
You just check a view and if view has two parents, right?
Maybe with your, maybe if this is...
document the problem if it's documented maybe we come up with a more explicit way to say okay this is how we want to represent this state but with all these it's kind of hard and i believe you have a good reason to do it like that but maybe it can be done differently and documented better 

**Geohot** [00:21:00]
yeah no i totally understand what you're saying about why there's a buffer on each one because there was a buffer on each one at lazy buffer it's definitely true uh but yeah no like like
Maybe another way to think about this is if you can fix problems at the abstraction layer of documentation, you move so much faster than actually implementing all this stuff, getting it to pass all the tests, and then being like, wait a second, we don't even need to write that.

**Qazalin** [00:21:18]
I agree.
Yeah.

**Geohot** [00:21:21]
Yeah, I mean, my rough proposal is something kind of like a... Because you're right.
A fundamental problem when you're doing graph rewrites is saying, how do I know which UOP belongs to which tensor?
And I mean, something that seems like one way to do this is to just create tensor UOPs, is to put tensor UOPs in the graph, and then you have rules about how...
This solves the two tensors are actually the same buffer problem.
This solves the... It doesn't actually create the buffers yet.
You can create the buffers later, but you can keep around the place.
It's guaranteed to be the same thing at the input to each tensor UOp.
Do you think that makes sense?
Or do you think there's a...

**Qazalin** [00:22:08]
I think there's a better way to do this.
It's going back to how stunning MNIST works.
So like stunning MNIST, if that's the future, you really don't need to actually keep the intermediary buffers, like whatever it is, tensors that aren't scheduled, like the user didn't actually want to schedule to keep in the scope.
So what I'm thinking about is what would it take to actually just only guarantee that the ones that you pass, the outputs that you pass, those are the only ones that will have a buffer that will live long enough for the next scheduled call.
And everything else is rooted.

**Geohot** [00:23:03]
Yeah, I talk about this trade-off explicitly in [abstractions4](https://github.com/tinygrad/tinygrad/pull/8272/files).
That's actually my first open question.
It's what tensors should get buffers.
So you're saying only the tensor is specified in the realized gain buffers.

**Qazalin** [00:23:20]
Yes, only the ones synced.
Then you can use the sync position.
That's what I do right now.

**Geohot** [00:23:26]
I've thought more about the sync position thing, and I actually don't think it works.
I can show you where it breaks.
The problem with using the sync position is if you do a rewrite, you can duplicate things.
Imagine you do a rewrite that's, like, merging two things across a sync position.
You'll end up getting tons of graph stuck on the first one in the sync position.

**Chenyu** [00:23:55]
Let's also put this in the doc.
So we have, like, examples, right?

**Geohot** [00:23:57]
Yeah, yeah, yeah.
This is something that exactly, like, this is why it should be discussed in the doc layer, because I'm...
60% sure that doesn't work, and that you need something that's actually in the graph that looks more like a tensor UOP.
But I might be wrong.
60%.
So yeah, let's discuss this at the doc layer, and then we can, at the doc level, so we can, you know, before we go and write that code, because it works.
You're going to get the right answer.
The problem is it's very often going to redo a lot of compute.
And that's something we have to be so careful with here, too, because, like,
The tests barely test for this.
There's so many things where... Sure, we have some that count kernels, but there's so many things where... 

**Chenyu** [00:24:17]
We don't constantly use memory and, like... 

**Geohot** [00:25:18]
Yes.
We have some that count the memory, too, but... Yeah, they're not... I wouldn't trust them.
I wouldn't trust them, and they're in no way minimal.
They're just, like... We just shoved in a number for what it used to be.

**Chenyu** [00:24:59]
Yeah, yeah, yeah.

**Geohot** [00:25:00]
So what it used to be was any good.
Well...

**Chenyu** [00:25:04]
And a lot of these will usually go through the, like, discussing through the docs and having some examples.
It's a lot easier to think of examples when we were discussing it at a much higher level, or at least like class of examples that we want to solve.
That's also a good way.
These will eventually lead to a test that tests these controversial examples.
I think that's a much systematic approach.
We write this, we figure out something didn't work, we have a one-off test that tests this thing.

**Geohot** [00:25:41]
Yeah, yeah.
I think so much of this stuff... Again, that fundamental thing about what tensors get buffers, right?
I propose three options in my [abstractions4](https://github.com/tinygrad/tinygrad/pull/8272/files) doc.
I don't think also that these docs should just have one way of doing things.
The doc should enumerate three options, even if two of the options are almost straw men, to kind of say, well, you can't do this, right?
Like, I have one option there, give buffers to all tensors in scope.
Well, you can't actually do that, because that's just going to break all the folding.
Uh...
But why you don't want to make a best effort approach for others, that's less clear to me.
I think you might want to.

**Chenyu** [00:26:17]
Okay, sounds good.

**Geohot** [00:26:18]
But maybe you don't.
And if you don't, it makes things a lot simpler.

**Chenyu** [00:26:22]
Yeah, so we definitely don't want to slow everyone down by asking this.
But again, like the scheduler part, the buffer, the realize part is kind of very fundamental to the TinyGrad project.
So let's try to get this right.

**Geohot** [00:26:38]
Yeah.
Yeah, I think that's also a really good question to ask right there, maybe even before the const thing.
It's the, is it okay if only the tents are specified in the realized gain buffers?
How sure are you that that's okay?

**Chenyu** [00:26:55]
Well, that's just implementation details, right?
No, that's... No, you start with how people use it and expect it to work.

**Geohot** [00:27:02]
Exactly.
Yeah, yeah, yeah.
So what we do there is we go through 10 common use cases and we say, is this going to massively, like, is this going to violate anyone's expectation?

**Chenyu** [00:27:11]
Yeah.
And that's ultimately how we would decide, like, picking from these.
Yes, everyone has this trade-off.
Cool.
I think everyone is on board on this.
Let's move on to the next one.
new Gradient API?

**Geohot** [00:27:30]
So yeah, good thing I didn't waste a lot of time implementing things before I asked on Twitter.
So the new Gradient API itself is good.
I mean, the new Gradient API is very simple and clear.
And it turns out Torch actually has the same API.
But my idea of replacing backwards with that API is it looks like not so smart.
And I'm happy that I only wasted 20 minutes on it.
Because I asked and we got a response from Horace, one of the PyTorch maintainers.
And he's like, yeah, so you have to handle these four use cases too.
And I'm like, yeah, see, this is good.
So it's not that much effort to keep around backwards.
Yeah, I should have been a lot more careful before I just carelessly killed something that I think the Torch people put a lot of effort into.
So, you know, it's not like we ever actually deleted it.
But yeah, the one thing that is going to be a little bit TinyGrad specific, and that I've thought extensively about the trade-off around, is you were not going to be able to call backwards on a realized graph.
If you realize your loss, you're no longer going to be able to call loss.backwards.
And the trade-off here is we can do away with `tensor.no_grad`.
Like, there's this state in Torch called `tensor.no_grad`, and that won't keep around the context, which will free the memory as you go.
I really don't like that state.
because a lot of people often forget to do it, and then they waste tons of memory.
It's also separate from training.
There's `no_grad` in training, and they're separate concepts.
So as long as we're okay with calling backwards before you realize, you don't have to realize the backwards.
You just have to call backwards and construct the graph before you realize.
Then it's fine.

**Chenyu** [00:29:35]
How about explicit retain graph or something like that?

**Geohot** [00:29:42]
a retain graph after you call dot backwards.
We don't need that either.
The graph is always retained.
Again, because all this stuff is all done on unrealized tensors, this is all just not a problem.
I'm 95% confident in this being the way to go.
And if anyone has objections, now's the time to state them.

**Chenyu** [00:29:53]
No, people won't have enough to say no.

**Geohot** [00:29:54]
Well, if someone has a very... I know, but if someone has a very... I just think that you're going to have to... I mean, TinyGrad is moving towards everything not... 

**Chenyu** [00:29:58]
I think you will realize all the problems after you rewrite most of our current training examples to... 

**Geohot** [00:30:00]
Oh, this doesn't change the training examples.
There's only like two examples that are actually broken where loss is realized before backwards call.
I didn't write them to opt and loss.
That's aggressive.
But no, this one is just a tiny change.
There's a few tests that have to change.
But I think it's definitely the way to do it.
So the new gradient API is the old gradient API with this new caveat.
And then we can delete all the `no_grad` stuff.
And you have this extra function, which already works, called `tensor.gradient`.
And yeah, it's the same as PyTorch, `torch.autograd.grad`.

**Chenyu** [00:31:04]
Yeah, I think it's pretty cool.
I was just writing some dumb functions and tried to call a gradient on it to see if anything breaks.
Or it should work at its level.

**Geohot** [00:31:16]
Yeah, also, we now support second derivatives.
So that's cool.
Second derivatives just work.
You can.

**Chenyu** [00:31:21]
Yeah, there's an updated test case for second derivative.
If you really want, you can do multiple order of derivatives.
And you can take gradients on gradients on gradients.
And that should just work.

**Geohot** [00:31:33]
Yeah.
One of the other trade-offs that I made was I added movement ops into the big graph.
And you kind of have to do this because computing the derivative of an arbitrary view is really tricky.
Like...
I struggled with it for five hours.
There's no way to do it cleanly because the problem is some things are very simple and they're no problem, but when you do basically the stuff that Conv is doing with these overlapping... Yeah, when you have overlapping axes, then computing the gradient of that view is really tricky.
So, you know...
recovering that structure.
There's no point.
We'll just keep around the real structure that created it.
And then the derivatives of the six primitives, like reshape, permute, the others are so easy.
So, yeah.
We have movement ops in the big graph.

**Chenyu** [00:32:33]
Isn't it nice that we keep all the two movement ops thing and make it still working?

**Geohot** [00:32:39]
Oh, yeah.
Yeah, yeah, yeah.
I did get a view gradient working at least 95% of the time with two movement ops.
There's bugs in two movement ops.
I see.

**Chenyu** [00:32:49]
Okay.
Cool.
Okay, let's move on.
I think the next one we already discussed, we are going to continue working on this at a higher level.

**Geohot** [00:33:00]
Yeah.
Oh, Tensor is UOP.
Yeah, I'll write some more in [abstractions4](https://github.com/tinygrad/tinygrad/pull/8272/files) about this.
Ideally, you want Tensor to be the place where UOP is connected to Buffer instead of in some random dictionary.
So, yeah, we'll see if that's possible.

**Chenyu** [00:33:16]
Okay.
The next one is some smaller items that I'm working on.
One is OPS.POW.
We want this because the current implementation doesn't work for Integer.
And for this to happen, I was waiting for the new gradient stuff.
So it's easier to write the correct thing there.
But I think it's pretty cool that if you do a tensor,
power to integer or integer power to another integer.
Sorry, I should say tensor power to a const integer and a const integer power to integer buffer, not const.
These should be folded and the code is there.
I just need to write more tests to making sure that's correct.
This has the benefits of it delegates some of the NAN logic that we specifically write in the tensor.py level.
And that should be handled by device.
If it returns NAN, then it's NAN.
And because of the new gradient stuff, now is a good time to fix all the stability of some activation functions like sigmoid.
So most of these questions are coming from sigmoid function or hyperbolic sine function.
It's because you have 0 multiplied by infinity.
So the way we express it, if it end up to be really evaluating 0 multiplied by infinity, then it will be NAN.
because that's how the spec works.
But sometimes this is 0.
Sometimes it's a fixed const.
So the way I did it is in a rewrite level for patterns like this.
So it's basically a reducible rewrite of this 0 multiplied by inf such that you get a fixed value.
It's done for the current way we implement sigmoid.
But there are different ways to write sigmoid.
If you write it slightly differently, then it doesn't work.
And I don't really like that.
I think it should work for most of us.
So basically, a principle way to think about in what case we want to take rewrite into 1 over x and in what case we don't.

**Geohot** [00:35:52]
I mean, to give an example, I'm not exactly sure if this is exactly what you mean.
But if you have x and x is infinity and you're multiplying x times x reciprocal,
That's 1?

**Chenyu** [00:36:01]
Yeah, so the problem is when you say 1 plus 1 over x, how do you want to fix it?
Do you want to fix it by rewriting that to x plus 1 divided by x?

**Geohot** [00:36:14]
No, you can't do that.
That fixes it for one direction of the limit, not the other direction.

**Chenyu** [00:36:22]
Yeah, so...
That's what I mean.
And there are also cases that we previously didn't handle.
I put a test on this a while ago.
So there are a lot of underscore extreme that test a very big value.
Basically, if you have any intermediate, let's call it exp2.
But on a very big number, you've got an infinity there.
And only until you can somehow rewrite that to be not infinity.
it won't be safe.
It won't be stable.

**Geohot** [00:36:53]
Is this called renormalization?
I know the physicists love this thing.

**Chenyu** [00:36:57]
I don't know.
Sometimes it's tricky.
Sometimes you really need to write it in the softmax safe way.
So you need to first get the max and you subtract the max.
There's no rewrite rule that will rewrite your softmax to be stable.
You need that explicitly.
But anyway, that is half done.
The final one is I'm cleaning up the view reshape.
I think the reshape function is fine now.
In the view adds function, there's this complicated mask logic that sometimes decides to project the mask, sometimes it doesn't.
That's the part I want to clean up.

**Geohot** [00:37:38]
Can we get you a symbolic for that?

**Chenyu** [00:37:40]
It's the same problem that it's hard to...
get the derivative of arbitrary view now you have arbitrary expression ask what what's this what's the movement that generates this symbolic expression it's like maybe possible you can maybe get that 

**Geohot** [00:37:50]
Would you rather fold it all with movement ops?

**Chenyu** [00:37:55]
No, I think we want to do this as early as possible to reduce the total views and just how big it is.
Otherwise, we can keep everything, right?

**Geohot** [00:38:14]
Well, yeah, yeah, no, but we can now, like, it's now pretty easy if you want to use rewrite rules on movement ops, right?
Like, if you have, like, a reshape followed by a permute or something, you could... 

**Chenyu** [00:38:25]
Eh, maybe.
It's probably not worth it.
It's another concept.
We have much, we have other things that we can work on.
Okay, the next one is some broadly what we want to do in midterms, middle terms.
So not this week, but more like next month or so.
The three things I put, one is how do we deal with lines?
Do we have lines?
Do we need more?
Another is we talk about what GPU we want to target.
And the final one is TidyGrad is very slow for you.
The Python time is bad.
Some kernel is bad.
We want to improve that.

**Geohot** [00:39:06]
All right, so the lines is when AM is finished, I think we won't...
I think we'll bump the line count to get AM in if we're not done by then.
We're both racing the clock here.
I will bump for AM.
We'll get AM and DSP in in one day.
I've got to bring DSP back.
I bought some.
They should be here today.
I'm very excited.
I got some USB GPU adapters.
Hopefully our driver works.
You see the chip I linked?

**Nimlgen** [00:39:49]
Yeah, I've seen it.

**Geohot** [00:39:51]
Yeah, so they're... The GPUs are only supposed to work over Thunderbolt, because Thunderbolt actually maps the memory.
Thunderbolt or USB4.
But the chip supports USB3.
So... Hopefully it's just doable, and doesn't require patching the firmware of the chip.
But, uh...
Yeah, no, I think that'll be really cool because we could sell a product where we have external GPUs that you plug into a Mac and they just work in user space.
USB is user space.
You can write USB drives in user space.
It'll be like kind of another layer of encapsulation where we encapsulate all the... How are we going to do that?
Because you're not really going to be able to mmap it.
Maybe you do a trap handler?
Put it on the USB?
Yeah, or some function we can override, some accessor.

**Nimlgen** [00:40:53]
Yeah, maybe.

**Geohot** [00:40:54]
Yeah.

**Nimlgen** [00:40:55]
We already have a trap handler for memoryview.

**Geohot** [00:40:59]
Oh, great.
Oh, yeah, yeah, for the testing.
Yeah, so I will plug two of them in to computers and make sure you have access.
yeah Chinese GPU yeah you know AMD desires mediocrity and they always will I post this stuff on Twitter and people are just like George you do understand they've been saying they're going to make their drivers good for 15 years now right so you know eventually fool me once and all that so
I think probably a tape out is a long, long, long way away.
I think there is a good intermediate step here, which I'm hoping that these Chinese GPU manufacturers are serious.
And, you know, they're hungry in a way that AMD is not.
So, yeah, well, moore threads, biron.
I'll see what chips I can buy.
And, yeah, we can get some random Chinese GPU manufacturer on MLPerf.
Hopefully they'll be more excited about it than AMD.
And then for improving speed, yeah, we got to get through the lazy stuff first.

**Chenyu** [00:42:21]
Yeah, so that's why.

**Geohot** [00:42:24]
Yeah.
we get through the lazy stuff and then I mean some of it can just be done by improving the speed of the pattern matcher but I think there's also some lower hanging fruit than that which is just like how often are we just being stupid in the pattern matcher and matching way too many things I bet that you could double the speed by like going through the things and saying like oh yeah I don't actually need to do that that's matching way too often so

**Chenyu** [00:42:53]
Okay, great.
Okay, moving on to open bounties.
I can speak for ONNX.

**Chenyu** [00:43:05]
ONNX is moving.
I added a small milestone to...
test.
I just put it as support top 100 on X model.
Just find a way to define what's top 100 and find a way to test that we are really supporting those 100.
I think it's good enough.
So the context is after we put comma to use the tinygrad on device for layer runners, we also want to make their
roll out the code they use for generating data to use tinygrad.
And the easiest way to start is they will, similar to open pilot model, they just export their thing as an ONNX model and we run it and then can benchmark it and see if it's faster.
I think this is a much realistic way than ask them to rewrite all their stuff in TinyGrad first and see if it's too slow or something.

**Geohot** [00:44:03]
I really like this.
I really like this 100 ONNX model.
What was the bounty set at?

**Chenyu** [00:44:08]
Is it 200?

**Geohot** [00:44:09]
I think we can increase the bounty a little bit.
I think we can go to 400 for that.
Okay, 400.
Yeah, if we support the top 100 Onix models and there's a tester for that?
Yeah, I think.
I just don't know how much we already support, right?
We already support them.
I just shouldn't say, you know what?
400.
I doubled the bounty, but I will change it to support test top 100 ONNX models.
I want to test this in CI.

**Chenyu** [00:44:37]
Oh, that wasn't implied.

**Geohot** [00:44:38]
Well, if it was already implied, then it's already implied.

**Chenyu** [00:44:41]
Okay, it's double, so... Yeah, it's a double the bounty, but... But you got the idea.
We want to support most of them.
I understand that in the ONNX spec, there are some very weird ones that we would never care about, and we'd probably not be able to do anyway, but we want to support...
almost all of them.

**Geohot** [00:45:01]
Yeah, we want to support the top 100 model.

**Chenyu** [00:45:03]
And the importance for this bounty is we have a script and we have a way to verify we do support top 100 of that, even if, like, I don't know, next month the top 100 change, we probably need to detect that and know this.

**Geohot** [00:45:16]
Yeah.
And then, oh, well, the other, yeah.
How many lines do we need to move ONNX out of extra?
What are we down to now?

**Chenyu** [00:45:25]
Probably a ballpark of a few hundreds.

**Chenyu** [00:45:30]
There are a few big functions.
I think he has a much better idea.
A few hundred is my guess.
Not for the ONNX runner or things like that.

**Geohot** [00:45:44]
No, yeah, yeah, yeah.
And then what is it also going to take to get rid of our dependence on its proto buffs?
To get rid of our dependence on ONNX?
Yes, there goes a proto buff.

**Chenyu** [00:45:54]
Yes.
We'll see.

**Geohot** [00:45:55]
I mean, yeah, it should be in TinyGrad with nothing, ideally.
But no, that's later.

**Chenyu** [00:46:03]
So let's make sure it's running correctly.
I also know that in the current ONNX compliance test, it's not complete.
It's poorly covered for some functions, and we already find bugs.
That's not covered.
So I think it's also working on improving the test coverage in addition to ONNX compliance test.
I think that's moving along.
Okay.
TensorFlow course.


**Ignaciosica** [00:46:40]
Hi.
Hello.
I've been cleaning up the PR for TensorCores 3.
Sorry, the swizzling the store.
And it's getting pretty clean for me.
I will up the PR to the main repo once I write the docs for the swizzling and all that.
I think I'm close.

**Chenyu** [00:47:05]
Are you blocking any ways to test the Intel stuff?

**Ignaciosica** [00:47:12]
I haven't.
I was actually going to do that today, to tackle Intel, because I finished all the others cleanly.

**Geohot** [00:47:29]
We've got to build some rainbow tiny boxes and just have one of each GPU.
We'll build some rainbows.
A 4090, a 3090, an Intel, a couple generations of AMD.

**Chenyu** [00:47:43]
Yeah, so my main point is if you hit some problems, you can access certain hardware.
You just ask somewhere and we will find something.

**Geohot** [00:47:52]
Yeah, we can definitely test on Intel for you.
Yeah, if you're confident, it's good if it passes all the other tests.
But cool.

**Ignaciosica** [00:48:04]
Sorry, I missed that.
If it passes all the other tests, what with Intel?

**Geohot** [00:48:09]
If the last blocker is Intel, I can get an Intel machine stood up here, and I can test things for you, even before we have rainbow tiny boxes.
So yeah, don't let that be a concern.

**SPEAKER_00** [00:48:20]
OK, sure.
For now, I rely on the emulated tests.

**Geohot** [00:48:29]
Yeah, I think the emulated test should be pretty good.
If there is some discrepancy between the emulated and the non-emulated, then yeah.

**Chenyu** [00:48:41]
Fast gemm was for flammit, but he's not here, so let's skip.

**Geohot** [00:48:45]
I could say a little bit about it.
Yeah, flammit came to the comma holiday party.
We talked a bit about fast gemm, and it's cool what it is.
It's
It's going to be exciting when we get to this, and this is going to be a big thing next year.
By the end of next year, we should be faster than Torch on NVIDIA.
The tricks are simple.
It's basically forms of double and triple buffering and local buffers.
We'll make it work.

**Chenyu** [00:49:13]
Okay.
Matcher speed.
Is that happening?
No?

**Geohot** [00:49:20]
I unlocked the matcher speed bounties.
There's up to $2,500 if anybody can 8x the speed of the matching engine.

**Chenyu** [00:49:32]
Can you also add something about the script that you're going to evaluate this?
Like 2x, 4x?

**Geohot** [00:49:40]
Yeah, the benchmark schedule.
But you can evaluate the speed.
If you're not capable of evaluating the speed, you can't
You can't... External benchmark schedule is a pretty good evaluation.
The matching engine right now uses a lot of if statements.
If you can compile it and replace it with dictionary lookups, that's going to be a lot faster.

**Chenyu** [00:50:08]
OSX GPUOcelot.

**Geohot** [00:50:10]
Yeah, we got someone kind of working on that.
I mean, we also have to get in the HCQ file abstraction, but I'd love to be able to test AMD and NVIDIA.
I mean, NVIDIA particularly because we have PTX.
If Ocelot compiles, we should be able to get a full NV testing working on OSX.
Yeah.
How far along is that PR?

**Chenyu** [00:50:34]
It's just a bunch of patches, and Nimlgen ask if those can be upstream.

**Geohot** [00:50:41]
Yeah.
Upstreaming them would be great, but then also make it so it actually runs, right?
It's not just GPU Ocelot.
It's also actually running NV entirely.
Yeah.
Oh, I see that, yeah.
There's a test in here.
Does it work?
Does it pass?
That's cool.
Wait.
How'd they do this?
It doesn't use NV, then.
Does it use NV?
Cool.
Yeah, I'll definitely lock it.
I'll definitely lock it.
Wait, what?
How is mock GPU working on OSX?
No, this isn't ready.
How does this work?

**Chenyu** [00:51:58]
Okay, post your question there.

**Geohot** [00:51:59]
Yeah, yeah, yeah.

**Chenyu** [00:52:03]
int64 indexing.

**Chenyu** [00:52:07]
I see 3PR now.
The first two was not correct.
The latest one seemed to be correct, but it needs more testing.
And have you reviewed any of those?

**Geohot** [00:52:18]
No, I haven't looked at all.
This one?
Should I lock it?
I'll lock it.
It's kind of in the right place.

**Chenyu** [00:52:31]
Yeah, so I think this way is the correct approach.

**Geohot** [00:52:34]
Yeah, that's where I put it.
Yeah.

**Chenyu** [00:52:36]
Yeah, so that one needs some more tests and I think there are tricky things in this.
It's like, what if you have a const and that const is bigger than int64 or something like that.
And it needs to justify if you want to do that for a negative
bound as well it only tests for max but you can imagine the intermediate can be negative if you have a like minus like a negative on that okay uh
Yeah, that's all I have on it.
Do you have any questions?

**Geohot** [00:53:19]
Can you click on... Yeah, I think, and I added one bounty too.
If somebody can get TinyChat running in WebGPU, basically TinyChat in browser, $1,000.
Do you think you could test versus ORT instead of Torch?
Yeah, that's fine.
Yeah.
We could definitely include ORT in the tests.

**Chenyu** [00:53:29]
Oh, ORT should be already?
I don't know.

**Geohot** [00:53:31]
Message from likely spammer?
Steam gift?
What?
What, a Steam gift?

**Geohot** [00:53:59]
Um... Oh, uh, do you want to say something?
For the Sieds Lykles?

**Geohot** [00:54:04]
Oh, not sure your mic is working.
I don't hear you.
I think you're a speaker.
If I gave you speaker, I didn't take that away from anybody.
Yeah, you're a speaker.

**Chenyu** [00:54:13]
Oh, I didn't include your bounty.
Sorry.

**Geohot** [00:54:21]
Yeah, Sieds, you should be able to talk.
Oh, those messages are from last week.
Okay.
Great.

**Chenyu** [00:54:28]
That's it.

**Geohot** [00:54:29]
Thanks, everyone.

**Chenyu** [00:54:30]
Bye.
See you next week.
