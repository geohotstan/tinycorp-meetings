# 2026-06-01 Meeting

### Meeting Agenda

**Time:** new meeting #22, 6/01 9am Monday San Diego time
- company update
- SLICE (SHRINK), ParamArg, dtype.vec
- CI changes
- unique_const, const, invalids
- VIZ
- MLPerf LLaMA
- HCQ2
- bounties, issues, Comma happiness


### Audio

[Youtube Link](https://youtu.be/FX3N0LiOwOs)

### Highlights

- **[Company Update](#geohot-000011)**: Tinygrad had a strong sales month, nearly reaching $1M, and secured Blackwell cards at an $8,700 price before prices rose to about $10,700.
- **[GPU Launch Architecture](#geohot-000200)**: Geohot argued that CUDA-style APIs and multi-process GPU control add complexity, while tinygrad should move toward directly manipulating GPU command buffers and doorbells.
- **[HCQ2 Vision](#geohot-000425)**: HCQ2 could eventually launch work hierarchically across massive GPU clusters, where one machine triggers others instead of pre-launching huge process grids.
- **[Shrink / Slice Refactor](#geohot-000527)**: Slice is being replaced by shrink semantics using offset and size, which simplifies symbolic shrink cases and aligns with buffer view behavior.
- **[ParamArg and dtype.vec Removal](#geohot-000527)**: `ParamArg` now centralizes parameter metadata, and Geohot described a path to removing both `dtype.vec` and `PtrDType` through renderer-level rewrites.
- **[Renderer Compliance Tests](#geohot-000954)**: The goal is a clean renderer/codegen abstraction where backend correctness is covered by compact compliance tests for ALU, load/store, loops, and conditionals.
- **[Invalid Padding Semantics](#geohot-001159)**: Padding should use invalid values instead of zeros, allowing invalids to be ignored in reductions and replacing multi-style sharding with pad-invalid semantics.
- **[CI Improvements](#chrism-001813)**: CI for tinygrad collaborators moved to faster Namespace runners, most tests now finish within about three minutes, and `getenv("CI")` was mostly removed.
- **[Const and Invalids](#chenyu-002205)**: Tensor creation APIs now distinguish buffer-backed values from fused consts, while `unique_const` remains only for invalids until deduplication issues are resolved.
- **[VIZ Updates](#qazalin-002939)**: VIZ now shows address-space color boxes for UOps and lets users toggle everything client-side, including consts that were previously hidden.
- **[MLPerf LLaMA Profiling](#qazalin-003128)**: Tinygrad launches about 11,000 kernels versus AMD’s roughly 3,000, so the LLaMA speed project is focused on identifying missing fusions and matching AMD kernel behavior at higher abstraction levels.
- **[HCQ2 Schedule Rewrite](#nimlgen-004135)**: HCQ2 was rewritten as a single pass over the full schedule, eliminating multi and moving dependency tracking out of `HCQ2Graph`.
- **[70B Training Bottleneck](#wozeparrot-005505)**: The 70B run is slow, with optimizer work taking around 50 seconds on CPU and MFU around 3.3, prompting investigation into CPU/GPU memory movement and optimizer placement.
- **[MLPerf Submission Status](#wozeparrot-010229)**: MLPerf reviews are complete with no major complaints, and the late-added precision logging requirement has been added to tinygrad’s logs.

### Transcript
##### **Chenyu** [[00:00:00](https://youtu.be/FX3N0LiOwOs&t=0)]
Let's get started. I'm still a little bit sick, so I will do less talking today. And we can start with company updates.

##### **Geohot** [[00:00:11](https://youtu.be/FX3N0LiOwOs&t=11)]
Big sales in the last two weeks. I sent out an email like two weeks ago. I did a little bit of marketing. It's worked really well. I think we brought in like... We almost did a million dollars this month. So that's cool. We got our order in at the last minute for Blackwell cards.

##### **Geohot** [[00:00:37](https://youtu.be/FX3N0LiOwOs&t=37)]
At a $8,700 price.

##### **Geohot** [[00:00:41](https://youtu.be/FX3N0LiOwOs&t=41)]
Now they've gone up to like $10,700. So yeah, the price went up accordingly. I just sent a 50k wire to memory.net. I probably got like three sticks of memory. Elon followed us.

##### **Geohot** [[00:00:59](https://youtu.be/FX3N0LiOwOs&t=59)]
That's somewhat exciting.

##### **Chenyu** [[00:01:03](https://youtu.be/FX3N0LiOwOs&t=63)]
Right, MLPerf?

##### **Geohot** [[00:01:09](https://youtu.be/FX3N0LiOwOs&t=69)]
I wouldn't work with Elon. Yeah, Elon... Like... He would...

##### **Geohot** [[00:01:23](https://youtu.be/FX3N0LiOwOs&t=83)]
I think this is the problem with Elon and AI. Like he pushes for targets that are like... Clear metrics. And this stuff works in space. And this stuff works in electric cars. But I don't think it works for social networks. I don't think it works for AI. So...

##### **Geohot** [[00:01:43](https://youtu.be/FX3N0LiOwOs&t=103)]
Yeah, I don't know. I don't think anything actually comes of that.

##### **Chenyu** [[00:01:47](https://youtu.be/FX3N0LiOwOs&t=107)]
But... Just interesting. And certainly the things they are trying to write. They want to be able to write such things using... tinygrad one day.

##### **Geohot** [[00:02:00](https://youtu.be/FX3N0LiOwOs&t=120)]
Yeah, I mean... I have an idea that like... Yeah, what they end up with is... I don't know how low level they are going into the driver. Right? They are probably still using the whole CUDA stack. They are just writing it in C. And like, you know, dealing with... The thing about these stacks is... There is so much that you have to do because the rest of the stack is bad. For example... There is no way... If you are driving an 8 GPU system... You really need like 8 processes in order to do that. And... Like, sure, you can in theory drive it from a single process. But if you are CUDA and queue kernels, is it all slow? I mean, maybe you can do this with graph capturing. And like maybe it kind of... The NVIDIA thing does this for you. But... I think you really are super limited by these APIs. And unless you are thinking... In terms of like... Okay, so what is actually manipulating the GPU doorbell? What is building the command buffer? What is... CUDA Graph allows so much stuff that it is clearly not just like pre-building a command queue. It is running some interpreter and... Yeah, like what is that actually doing? So... Yeah, no, I don't even think that... I think that Elon is even going to realize after he writes a script... And he writes his whole thing in C... That he is still left with a lot of the same... Not necessarily bottlenecks. Because you can deal with all these bottlenecks with complexity. You can deal with all these bottlenecks by saying... Okay, well, we are going to have a process per GPU. Okay, but now you need something to synchronize those processes. Now one of those processes is going to be OOM-killed. Okay, now what happens, right? So it is just... It is a lot of stuff that you have to deal with versus just saying... The GPUs are just mapped in some address space. And, you know, we compile a small program that directly just... You know, pokes that address space. To the point that you could even have the GPUs all drive themselves. And... I mean, it is all kind of weird. It all gets kind of like weird to think about, right? It is like one of those like... I am playing Slay the Spire. And it is one of those like you set one card down. And that card puts a... Puts a combo in motion. Which, you know, actually plays 50 cards, right? And you could imagine the exact same thing with these...

##### **Qazalin** [[00:04:24](https://youtu.be/FX3N0LiOwOs&t=264)]
These...

##### **Geohot** [[00:04:25](https://youtu.be/FX3N0LiOwOs&t=265)]
With where like HCQ2 goes. And you could imagine like... You know, even 100,000 GPUs. It is not exactly one computer driving 100,000 GPUs. But one computer tips the first domino over. Which tips over the next dominoes. But all those dominoes are set up within the tinygrad framework. Right? You don't pre-launch, you know, 100,000 processes using a Slurm cluster. You just like... You know... Poke the address space. Okay, one computer can't poke the address space. Okay, so one computer pokes the address space of 10 computers. Which themselves poke the address space of 10 computers. So on and so forth. You have this like hierarchy to the whole... The whole launch procedure.

##### **Geohot** [[00:05:07](https://youtu.be/FX3N0LiOwOs&t=307)]
So... That is eventually where these things go. Okay. Sounds good. Anything else for company update?

##### **Qazalin** [[00:05:20](https://youtu.be/FX3N0LiOwOs&t=320)]
Nope.

##### **Chenyu** [[00:05:21](https://youtu.be/FX3N0LiOwOs&t=321)]
Okay. Next. Still your thing. I just list bunch of things you added.

##### **Geohot** [[00:05:27](https://youtu.be/FX3N0LiOwOs&t=327)]
Cool. Yeah. So I didn't... Slice isn't new. Slice is just what used to be called buffer view. But I'm going to delete that. It's really just shrink. So I changed the semantics of shrink to have an offset and a size. And offset and a size now matches buffer view. So that's a lot nicer. I mean, offset and a size thing is a lot nicer for several reasons too. Because like many times... Many shrinks... Like when you're doing a symbolic shrink. The output size is fixed. But the offset is what changes. So when we used to express that in terms of begin and end. We'd have to put the symbolic in both things. And then you'd have to like make sure carefully that they cancel out when you compute the size. So... That's fixed with the new shrink. Thought about other things like crop. I think no. I think that this just starts to... You know... Like... Just make it a lot harder to reason about. Okay. Does this crop add a pad? Right now you're going to have to have a function which tells you that. So just keep them explicit. Did the refactor to `ParamArg`. `ParamArg` is basically... I used to be like trying to like stick sources on the params to express things. But it's not really right. `ParamArg` is just the... It's a dataclass that lives in the `arg` argument on `PARAM` and it specifies everything about that parameter. What slot it's in. What device it's on. What address space it's in. If it has a min and a max. Yeah. So this is just... And `ParamArg` I think can be reused for buffers as well. So yeah. I mean the difference between a buffer and a param is a buffer is a... Concrete piece of memory. Whereas a param is a... Is an unbound piece of memory. Maybe they collapse kind of the same thing. But they at least can have the same arguments. So yeah. `dtype.vec`. So okay. I finally have like a real approach to get rid of `dtype.vec`. And I'm going to get rid of `dtype.vec` and `PtrDType` at the same time. These things are both... They're just way too intertwined to try to get rid of one and not the other. Or to try to do this in pieces. I have it working. I have like a transformer... A rewrite which sits at the end of the main renderer rewrite. And rewrites into... I think which would just be like the renderer spec. In the renderer you can use three movement ops. You can use shrink. You can use index. And you can use stack. So yeah. You know you can see how shrink, index, and stack work. Shrink and index can work on globals. Stack can only work on registers. Well shrink and index can also work on registers. So shrink and index can work on both globals, locals, and registers. Stack can only work on registers. Clear spec. I made them the same color as the other movement ops. They're not special movement ops. Those ones are here to stay. So yeah. I see the path to getting rid of `dtype.vec`. It's one of these things that like... Okay you're like, oh I can just remove it. I can just use shape. Okay but what about the images? Okay but what about the pointer? So you know just going through the cases one at a time.

##### **Geohot** [[00:08:50](https://youtu.be/FX3N0LiOwOs&t=530)]
Making them not use `dtype.vec`. Eventually `dtype.vec` can all be removed. It's just like... Let's see.

##### **Geohot** [[00:08:59](https://youtu.be/FX3N0LiOwOs&t=539)]
But I also just... There's something about this project that's just... My least favorite kind of work to do. What do you mean?

##### **Wozeparrot** [[00:09:07](https://youtu.be/FX3N0LiOwOs&t=547)]
It's the best kind of work.

##### **Geohot** [[00:09:10](https://youtu.be/FX3N0LiOwOs&t=550)]
It's what?

##### **Chenyu** [[00:09:11](https://youtu.be/FX3N0LiOwOs&t=551)]
It's the best kind of work. It's the most important kind of work.

##### **Geohot** [[00:09:15](https://youtu.be/FX3N0LiOwOs&t=555)]
Oh maybe it's important. But it's just kind of my least favorite. I just kind of hate doing it. It's just very painful. And like at the end you're not even going to get anything. Like it's just going to like... I don't know. Maybe today if I write the compliance test. At least I'll feel like I'm doing something. Like a compliance test for a renderer. Like I'd like it to be like one test. That's pretty straightforward. And that test says, okay this renderer implements all the things correctly. Versus now, you'll run the tests. And a test will fail. Something like `test_gem_fp16`. FP16 will fail. Why does it fail?

##### **Geohot** [[00:09:52](https://youtu.be/FX3N0LiOwOs&t=592)]
Okay.

##### **Geohot** [[00:09:54](https://youtu.be/FX3N0LiOwOs&t=594)]
And then you have to like trace that back to what the renderer didn't implement correctly. Okay. So if we can truly draw a perfectly leak-free abstraction between the renderer and the codegen. Then hopefully that that just renderer compliance test can be the entire backend test. You know we'll have to roll this out carefully and slowly. But once we get to the point where no more backend tests ever fail. Unless the compliance test fails. Then we have that done. And yeah.

##### **Chenyu** [[00:10:31](https://youtu.be/FX3N0LiOwOs&t=631)]
How big do you think this compliance test will be?

##### **Geohot** [[00:10:35](https://youtu.be/FX3N0LiOwOs&t=635)]
Not that big. So it's all... Like with the removal of DType crap. It all gets a lot simpler. The dtypes were all like really hard to reason about. It was hard to reason about like things like GEP and like... There were just like... There were a lot of cases that could be in the old one. That are just like cases that can't be in the new one anymore. So I would say that the compliance test... Well so okay. I'm going to add a function to the renderer that says like is supported. And that takes in a dtype and an ALU. And it tells you... Or a dtype and an op. It can be any op including load and store. And it tells you if that op is supported for that renderer. That's where we'll run a decomposition layer. If we have any ops in the graph that aren't supported in the renderer. The decomposition layer will do them. Yeah so... Yeah I mean it can be fine to not have those ops supported. And then it'll just go through decompositions. But yeah. So I think there's like an ALU part of this compliance test. There's a load store part of this compliance test. There's a loop part of this compliance test. There's an if statement part of this compliance test. And that's it.

##### **Geohot** [[00:11:50](https://youtu.be/FX3N0LiOwOs&t=710)]
Yeah. Excellent.

##### **Chenyu** [[00:11:55](https://youtu.be/FX3N0LiOwOs&t=715)]
Oh you were saying something about multi.

##### **Geohot** [[00:11:59](https://youtu.be/FX3N0LiOwOs&t=719)]
Oh multi. Oh. Well that's not related to this. I know. Okay. But... So multi is... The pad that we have is wrong. So when we pad... We pad with zeros. We shouldn't pad with zeros. We should pad with invalid.

##### **Geohot** [[00:12:28](https://youtu.be/FX3N0LiOwOs&t=748)]
Okay. What do we do after we pad? Okay.

##### **Geohot** [[00:12:33](https://youtu.be/FX3N0LiOwOs&t=753)]
So... You can tell that it's wrong. Because like right now when you read the rangeify rules for pad. The rangeify rules actually insert a where. They insert a where. It's invalid. They insert a where to basically put that zero where that pad was. Right? And you have to like explicitly do that when you have that pad. But you could also just like... If you want the old behavior of pad. You can just put a where. And then rangeify won't have to do anything. Right? Like it shows that the pad spec is kind of wrong. But the other thing that invalid gets you is... So when you think about multi. Multi is basically pad invalid. So think about a... Like a matrix that's sharded across four devices. On one of the axes. Right? So let's say the matrix is 256 by 256. That's the whole matrix. So each chunk is 256 by 64. So every device is a buffer that exists on four devices. That's 256 by 64. Then you do a pad based on the device number. Right? And that's all you have to do. There's no add. There's no anything else. It's just a pad based on the device number. And that is sharding across the axis.

##### **Chenyu** [[00:13:46](https://youtu.be/FX3N0LiOwOs&t=826)]
So what holds these four things together?

##### **Geohot** [[00:13:53](https://youtu.be/FX3N0LiOwOs&t=833)]
Well, so like nothing. Right? They're just like... Like they're on four different devices. But they represent the four different pieces. Right? So you can imagine doing each of these... Oh, then there's a few things about invalid. Right? So if you're doing like... If you're reducing and there's an invalid. That invalid just has no effect on the reduce.

##### **Geohot** [[00:14:18](https://youtu.be/FX3N0LiOwOs&t=858)]
What do you mean by no effect?

##### **Geohot** [[00:14:21](https://youtu.be/FX3N0LiOwOs&t=861)]
Okay. So like if you pad something... Right? Like right now... Okay. So we can think about like pad. Right? So right now if you do a pad and then a reduce, that pad is never going to affect the sum. Right? If it's a reduce add. Right? But if it's a reduce max, the pad might affect it. Mm-hmm.

##### **Qazalin** [[00:14:44](https://youtu.be/FX3N0LiOwOs&t=884)]
So...

##### **Geohot** [[00:14:44](https://youtu.be/FX3N0LiOwOs&t=884)]
But definitionally, if we pad invalid, it never will. Because invalid is just ignored along reduction axes.

##### **Geohot** [[00:14:57](https://youtu.be/FX3N0LiOwOs&t=897)]
Okay.

##### **Geohot** [[00:14:58](https://youtu.be/FX3N0LiOwOs&t=898)]
Like that was always a slight weird thing. Right? And this... Yeah. This actually creates some like annoyances with multi as well. So the replacement for multi is pad invalid with device num. And you can also see how you can do any arbitrary... Like polyhedral tiling with that. Which you can't do in current multi. So current multi just has a single axis number that you can shard along. But say you want to shard... Say you want to take that matrix, that 256 by 256 matrix and put a 128 by 128 chunk on each of the four GPUs. You can see how you can express that as a pad. You can't really see how you can express that with the current multi. So... Yeah. And we have to define the semantics of pad such that that works. But I think that's also just all the correct semantics of pad. So...

##### **Chrism** [[00:15:44](https://youtu.be/FX3N0LiOwOs&t=944)]
Yeah.

##### **Geohot** [[00:15:45](https://youtu.be/FX3N0LiOwOs&t=945)]
That gets rid of multi. Eventually.

##### **Geohot** [[00:15:49](https://youtu.be/FX3N0LiOwOs&t=949)]
And that one also works for fragment. So like... TileLang. One of TileLang's innovations is this thing called `alloc_fragment`. And `alloc_fragment` is a... So it's a form of `DEFINE_REG`. But instead of defining the register on a single... Like single thread. It defines a register group across a whole set of GPU threads. It's called a fragment. That's basically multi. And you see how you can express that with a pad, right? So say I want to make like a... You know, a 16 by 16 tile out of 128 threads. Okay? So that's `DEFINE_REG` too, and then pad such that it creates that 16 by 16, you know, like kittens-style thing. And you can see that like, for example, when you do a store, all of the threads... Will only store to their two registers. Because all the other ones are invalid. And the invalid store is nothing. It's very beautiful. It works. It also... Like Harold was looking at this back at lunch. And he's like... Yeah. So I understand them all. But like why... What is slice and what is replicated? Why are these here? I'm like, okay, good. Those are the two that are going away. Right?

##### **Qazalin** [[00:17:10](https://youtu.be/FX3N0LiOwOs&t=1030)]
Yeah.

##### **Geohot** [[00:17:11](https://youtu.be/FX3N0LiOwOs&t=1031)]
So... Oh, yeah. Slice also... Yeah. So the last thing I have to do to actually get rid of slice and replace it with shrink is define a full semantics for bit cast. And I have that worked out. I just need to like... It's a little bit different around... So torch won't let you bit cast a scalar. But tinygrad will let you. So if you bit cast like a rank zero tensor... Say you have like a rank zero tensor that's a float and you bit cast it to half. It'll split and become, you know, a two tensor. And if you bit cast that back to float, it gets rid of the ones dimension and goes back to a scalar. There's one little piece of subtlety, but otherwise it behaves the same as torch. And that shape semantic for bit cast should work for everything.

##### **Geohot** [[00:17:56](https://youtu.be/FX3N0LiOwOs&t=1076)]
And that allows shape changing bit cast.

##### **Qazalin** [[00:18:03](https://youtu.be/FX3N0LiOwOs&t=1083)]
Yeah.

##### **Geohot** [[00:18:05](https://youtu.be/FX3N0LiOwOs&t=1085)]
That's good.

##### **Chenyu** [[00:18:08](https://youtu.be/FX3N0LiOwOs&t=1088)]
Okay. Moving on. Next is the CI changes.

##### **Chrism** [[00:18:13](https://youtu.be/FX3N0LiOwOs&t=1093)]
Yeah. So, I mean, hopefully you noticed an improvement in the speed of CI in your PRs. This only applies to people who are members of the tinygrad org. So I guess if you're not that, then you won't see it. But yeah, on master, it still runs on GitHub Actions CI. So, you know, we're not going to be totally blind to like if something breaks there, but doesn't break on, you know, Namespace runners, then we'll be okay with that. Most of the tests finish within three minutes. There's still some that are slower than that, and the total end goal of this is to be under one minute. So still need some work there, but yeah, it's moving in the right direction. The other thing that people were complaining about last week was importing `test.ci` for CI, which no longer happens. `getenv("CI")` is gone completely. So that's good.

##### **Geohot** [[00:19:08](https://youtu.be/FX3N0LiOwOs&t=1148)]
Good to see.

##### **Chrism** [[00:19:09](https://youtu.be/FX3N0LiOwOs&t=1149)]
Nice. Yeah. And oh, no, sorry. There's actually one place that's still there. I don't remember off the top of my head exactly what it was. But it's all those. Delete it. It's probably not important.

##### **Geohot** [[00:19:23](https://youtu.be/FX3N0LiOwOs&t=1163)]
Yeah.

##### **Chrism** [[00:19:23](https://youtu.be/FX3N0LiOwOs&t=1163)]
It's always CI.

##### **Geohot** [[00:19:24](https://youtu.be/FX3N0LiOwOs&t=1164)]
It's always CI.

##### **Chrism** [[00:19:25](https://youtu.be/FX3N0LiOwOs&t=1165)]
OK. I think it's something like printing or something like that. It's like a debug printer or something like that.

##### **Geohot** [[00:19:29](https://youtu.be/FX3N0LiOwOs&t=1169)]
It's always CI. OK.

##### **Chenyu** [[00:19:34](https://youtu.be/FX3N0LiOwOs&t=1174)]
So is the namespace just running the same thing but with much better machine?

##### **Chrism** [[00:19:39](https://youtu.be/FX3N0LiOwOs&t=1179)]
Yeah, essentially. It actually has less RAM, but the machines are faster and appear to be more reliable. And also, they have the nice UI for us. And we can see when something got OOM-killed, which is nice. Actually, it revealed a bug in the memory leak in WebGPU, which I fixed.

##### **Geohot** [[00:20:04](https://youtu.be/FX3N0LiOwOs&t=1204)]
Have the Macs moved yet?

##### **Chrism** [[00:20:05](https://youtu.be/FX3N0LiOwOs&t=1205)]
I have not moved the Macs. Do we want to do that? They multiply the CPU hours by 10 to use a Mac.

##### **Geohot** [[00:20:17](https://youtu.be/FX3N0LiOwOs&t=1217)]
Let's just make sure they're fast in GitHub Actions. OK. Yeah.

##### **Chrism** [[00:20:21](https://youtu.be/FX3N0LiOwOs&t=1221)]
Well, yeah.

##### **Geohot** [[00:20:22](https://youtu.be/FX3N0LiOwOs&t=1222)]
That's expensive. Yeah. Yeah. Mm.

##### **Chrism** [[00:20:26](https://youtu.be/FX3N0LiOwOs&t=1226)]
So I think we can make it fast.

##### **Geohot** [[00:20:29](https://youtu.be/FX3N0LiOwOs&t=1229)]
Totally under three minutes. The whole thing's got to be under three minutes. That's what I'm doing.

##### **Chrism** [[00:20:34](https://youtu.be/FX3N0LiOwOs&t=1234)]
Yeah, the Windows tests are much slimmer now. It's just `test_tiny.py`. I don't know. I know we have a couple people who use Windows. So I guess we'll have bug reports if something regresses there. And at least we're still doing all the backends that we support there. So it should be OK.

##### **Geohot** [[00:20:53](https://youtu.be/FX3N0LiOwOs&t=1253)]
Yeah, I think that's mostly it. Certainly, if there's issues that you encounter with testing, let me know. OK, cool.

##### **Chenyu** [[00:21:13](https://youtu.be/FX3N0LiOwOs&t=1273)]
So you say what's the triggering criteria for this? Is it by author or?

##### **Chrism** [[00:21:19](https://youtu.be/FX3N0LiOwOs&t=1279)]
Yeah. If you, it's actually not member. It's like a collaborator on the tinygrad org. Yeah. Oh, yeah. It's also worth pointing out that if you push twice to your PR, it'll cancel the job from the previous run, just because we don't want to spam, overload the runners. And then it'll make it slow for everyone, because there's a concurrency limit. So it is worth, if you see a little x, because your job got canceled. That's why.

##### **Geohot** [[00:21:48](https://youtu.be/FX3N0LiOwOs&t=1308)]
Just keep that in mind. Anything else? I don't think so.

##### **Qazalin** [[00:22:03](https://youtu.be/FX3N0LiOwOs&t=1323)]
OK.

##### **Chenyu** [[00:22:05](https://youtu.be/FX3N0LiOwOs&t=1325)]
Next is my stuff. So I made a bunch of changes. I changed it to const and unique const. And I also reverted some of it, because it broke invalids. So the current state is, if you do the `.full`, `.zeros`, `.ones`, and the `full_like`, `zeros_like`, `ones_like`, loads, it will give you a buffer. If you want the fused const, you can just do the same thing. There's a const. So just do that. I think I replaced most of them. Now it's a very clear distinction between you want a buffer or you want a const. And there's a way to write this.

##### **Geohot** [[00:22:55](https://youtu.be/FX3N0LiOwOs&t=1375)]
Yeah, I like the canonical thing of just doing assign zero. The Python const zero is a good way to write it, instead of doing like. Because you shouldn't assign zeros like. Just assign zero. That's fine. That does the right thing.

##### **Chenyu** [[00:23:08](https://youtu.be/FX3N0LiOwOs&t=1388)]
Yeah. I think we just have some of the old syntax that might be different. I tried to migrate all the ones in test that I can see. But if it's not tested, then I won't be able to.

##### **Nimlgen** [[00:23:23](https://youtu.be/FX3N0LiOwOs&t=1403)]
So for now, the unique const in spec still exists.

##### **Chenyu** [[00:23:29](https://youtu.be/FX3N0LiOwOs&t=1409)]
But it only exists for invalid. And I really need to think invalid and unique const kind of work. Not by design, but it works. So I'm thinking like how to better deal with this.

##### **Geohot** [[00:23:45](https://youtu.be/FX3N0LiOwOs&t=1425)]
We shouldn't need a unique const on invalid. Because there's no way to.

##### **Chenyu** [[00:23:51](https://youtu.be/FX3N0LiOwOs&t=1431)]
So there are some subtleties of this, especially with custom kernels. I'm pretty sure this is not by design. But this combination is kind of the only combination that can work now. The problem is which one do we really relax so that we can remove the unique const.

##### **Geohot** [[00:24:11](https://youtu.be/FX3N0LiOwOs&t=1451)]
Yeah. So I mean, I was wrong. I was wrong last week. I didn't really fully think it through when I said empty could be invalid. Obviously, invalid can't be a buffer. Because it's going in the like.

##### **Chenyu** [[00:24:26](https://youtu.be/FX3N0LiOwOs&t=1466)]
You want a unique property of that. Otherwise, everything just collides, right, with this empty.

##### **Geohot** [[00:24:33](https://youtu.be/FX3N0LiOwOs&t=1473)]
I think that should be OK. I'm trying to think why you need a unique const.

##### **Chenyu** [[00:24:41](https://youtu.be/FX3N0LiOwOs&t=1481)]
I would hate to have to keep unique const for that. So the goal is definitely remove that. But just to make this thing moving and reduce the scope of unique const for now is only limited to invalid. But the idea is to remove that.

##### **Geohot** [[00:24:57](https://youtu.be/FX3N0LiOwOs&t=1497)]
Yeah. I mean, yeah. Invalid should never be like all invalid should basically be the same. Whereas like all zeros are not quite the same because you can like update zeros. But like you shouldn't really be able to like.

##### **Chenyu** [[00:25:11](https://youtu.be/FX3N0LiOwOs&t=1511)]
I think there's just some issues with dedup. And if you have like multiple invalid that has the same shape, it points to the same UOp without our unique idea. It should be OK though.

##### **Geohot** [[00:25:32](https://youtu.be/FX3N0LiOwOs&t=1532)]
Yes, I think it should. It's not quite the same.

##### **Chenyu** [[00:25:37](https://youtu.be/FX3N0LiOwOs&t=1537)]
But anyway, so that's the current known part of this. Then also start to look into const with a device in its source. I have an open PR that kind of removes some of it and finds a new frontier that it has some issues. Oh, that's why I asked multi earlier because we have `MSTACK`, which is very annoying. It really doesn't like device in its source. So we still have like two producers that produce const with device in its source. We shouldn't have any user code that will introduce this. So those two are kind of the only two that need to fix. So yeah. One invalids, two consts with device, then after these, const will just be const.

##### **Geohot** [[00:26:42](https://youtu.be/FX3N0LiOwOs&t=1602)]
Yeah, that'd be great. So const notably, I did the address space derivation last week. And const notably doesn't have an address space.

##### **Chenyu** [[00:26:54](https://youtu.be/FX3N0LiOwOs&t=1614)]
Yeah, because it's always fused.

##### **Geohot** [[00:26:57](https://youtu.be/FX3N0LiOwOs&t=1617)]
Yeah, const doesn't have an address space. But even I also have things like special and define var not having an address space either. which I think is mostly fine.

##### **Geohot** [[00:27:08](https://youtu.be/FX3N0LiOwOs&t=1628)]
Yeah.

##### **Chenyu** [[00:27:09](https://youtu.be/FX3N0LiOwOs&t=1629)]
So another kind of nuance from this is anything that's coming from a fused const, like arange, notably won't have a device. So this is kind of a... These consts that have no device will only figure out their device when they ALU with another buffer or... Buffer is the only thing that can give you device. So I think I should put a good enough error message when you try to assign to like a deviceless stuff or errors that touches these devices. A deviceless const or its derivation, so like arange or eye, the EYE or things like that. But just let me know if you find something that's still weird at all.

##### **Geohot** [[00:28:10](https://youtu.be/FX3N0LiOwOs&t=1690)]
Yeah, no, I mean, that makes sense, right? And now with this makes sense, like it kind of synergizes with the `Tensor.zeros` fix because the `Tensor.zeros` now has a real buffer which has a device. But the...

##### **Chenyu** [[00:28:21](https://youtu.be/FX3N0LiOwOs&t=1701)]
This is also nice when we... So we used to have these problems when you like shard an arange on multi, it materialized and did a copy. Yeah. And things like that.

##### **Geohot** [[00:28:34](https://youtu.be/FX3N0LiOwOs&t=1714)]
Mm hmm.

##### **Chenyu** [[00:28:34](https://youtu.be/FX3N0LiOwOs&t=1714)]
Yeah. It's... It should be kind of a nice and usable and reasonable to work with.

##### **Geohot** [[00:28:45](https://youtu.be/FX3N0LiOwOs&t=1725)]
Yep.

##### **Chenyu** [[00:28:46](https://youtu.be/FX3N0LiOwOs&t=1726)]
Well, yeah. So that's pretty much it. I will continue working on these. And another minor annoyance is what's the torch backend? I try to make it work. It also doesn't like deviceless tensors.

##### **Geohot** [[00:29:03](https://youtu.be/FX3N0LiOwOs&t=1743)]
And I'm like, I'm fine just disabling the torch backend now.

##### **Chenyu** [[00:29:09](https://youtu.be/FX3N0LiOwOs&t=1749)]
I think it's easy enough for me to guard it somewhere.

##### **Geohot** [[00:29:14](https://youtu.be/FX3N0LiOwOs&t=1754)]
If it's easy. I don't know. I don't really care about the torch backend. I don't think anyone uses it. Not good. I think it's just nice.

##### **Chenyu** [[00:29:22](https://youtu.be/FX3N0LiOwOs&t=1762)]
I don't know. It's nice to know like where the designs differ.

##### **Geohot** [[00:29:28](https://youtu.be/FX3N0LiOwOs&t=1768)]
Yeah.

##### **Chenyu** [[00:29:28](https://youtu.be/FX3N0LiOwOs&t=1768)]
But I'd be okay with that.

##### **Geohot** [[00:29:30](https://youtu.be/FX3N0LiOwOs&t=1770)]
Either way. No.

##### **Chenyu** [[00:29:33](https://youtu.be/FX3N0LiOwOs&t=1773)]
But it's nice. It's nice. So let's close it with the last const. And we can move on to Viz.

##### **Qazalin** [[00:29:39](https://youtu.be/FX3N0LiOwOs&t=1779)]
Yep. Last week, I merged the changes you requested for VIZ. I mean, if there's more. So if you open this right now, you'll see little boxes that color the address space of the UOp. And also everything in UOps is toggleable on the client side. Previously, we used to just not show const, though. Now you can see that with a click. That's on the VIZ website.

##### **Geohot** [[00:30:14](https://youtu.be/FX3N0LiOwOs&t=1814)]
I see that CALL expands differently from the other ones.

##### **Qazalin** [[00:30:19](https://youtu.be/FX3N0LiOwOs&t=1819)]
Yeah, because I think you usually want to expand CALL.

##### **Geohot** [[00:30:23](https://youtu.be/FX3N0LiOwOs&t=1823)]
I think it's fine.

##### **Qazalin** [[00:30:25](https://youtu.be/FX3N0LiOwOs&t=1825)]
The shape is different. The shape is easier to click on. At the expense of the layout, it's a little bit less dense. Because then it just takes up more space. I guess it's fine for CALL.

##### **Geohot** [[00:30:39](https://youtu.be/FX3N0LiOwOs&t=1839)]
That's cool with the address space. You can see immediately when things are entirely derived from const that they don't have an

##### **Geohot** [[00:30:45](https://youtu.be/FX3N0LiOwOs&t=1845)]
address space.

##### **Qazalin** [[00:30:51](https://youtu.be/FX3N0LiOwOs&t=1851)]
I think you also changed the color of index to be more dots.

##### **Geohot** [[00:30:55](https://youtu.be/FX3N0LiOwOs&t=1855)]
Yeah, index is a normal movement op. We shouldn't treat index as special.

##### **Qazalin** [[00:30:59](https://youtu.be/FX3N0LiOwOs&t=1859)]
Yeah.

##### **Geohot** [[00:31:00](https://youtu.be/FX3N0LiOwOs&t=1860)]
I mean, yeah, we eventually need to add index support to rangeify. I don't think it works in rangeify right now, but it might. I don't know. Yeah, I mean, we should just be able to use index kind of like a gather anywhere.

##### **Geohot** [[00:31:19](https://youtu.be/FX3N0LiOwOs&t=1879)]
Yeah, this comes in line with...

##### **Geohot** [[00:31:22](https://youtu.be/FX3N0LiOwOs&t=1882)]
Yeah, how's the LLaMA speed project going?

##### **Qazalin** [[00:31:28](https://youtu.be/FX3N0LiOwOs&t=1888)]
So I have a REPL to profile and disassemble and trace every single kernel AMD runs. So I started today, this morning, working with an agent. I'm going to start first with the BF16 kernel and then move down to getting our kernels to match AMDs. The details, the detail breakdown is in the MLPerf channel. But at a high level, we are launching 11,000 kernels and they're only launching 3,000. There's like a huge gap to fill in and figure out exactly where we're missing fusions. I think it's explainable where we're having that 300 millisecond gap. It's also interesting that they use three different variants of the BF16 GEMM. There's three GEMMs that run on LLaMA. And they do these different variants and bake in the transposes. We do a bunch of layout stuff in between. Yeah, it's all these little stuff.

##### **Geohot** [[00:32:47](https://youtu.be/FX3N0LiOwOs&t=1967)]
Yeah, I mean, I would imagine our a lot of our synchronization stuff is just kind of slow.

##### **Qazalin** [[00:32:53](https://youtu.be/FX3N0LiOwOs&t=1973)]
Oh, yes, our gather is very slow. I have I have a fix for it. It's a custom kernel.

##### **Geohot** [[00:33:02](https://youtu.be/FX3N0LiOwOs&t=1982)]
But yeah, but yeah, I mean, just make sure again, the goal of this project isn't just to get, you know, the two hour time, the goal of this project is to get the two hour time in as high a level of abstraction as we possibly can. So you know, just just like importing their HIP kernels and importing their assembly kernels isn't that useful. The idea is that we have to figure out like, like, okay, so first for each one of these kernels, can we write it in UOps and get the same time? Then if we can write it in UOps, how come we can't write it in tensor? Right, and then improving these things as we go like, okay, why is why is rangeify not hitting that fusion, like that kind of stuff?

##### **Qazalin** [[00:33:45](https://youtu.be/FX3N0LiOwOs&t=2025)]
Yeah, I think that's gonna be my approach. Other than the GEMM, which I think really needs assembly. For the other ones, I'll try to get...

##### **Geohot** [[00:33:53](https://youtu.be/FX3N0LiOwOs&t=2033)]
Yeah, you can just for the GEMMs if you want. Sure, whatever. But that's already kind of what the baseline is for the GEMMs. That's fine.

##### **Qazalin** [[00:34:03](https://youtu.be/FX3N0LiOwOs&t=2043)]
But the other ones they use mostly Triton to write those kernels.

##### **Geohot** [[00:34:10](https://youtu.be/FX3N0LiOwOs&t=2050)]
Is what?

##### **Qazalin** [[00:34:11](https://youtu.be/FX3N0LiOwOs&t=2051)]
Triton.

##### **Geohot** [[00:34:12](https://youtu.be/FX3N0LiOwOs&t=2052)]
Oh, they use Triton.

##### **Qazalin** [[00:34:14](https://youtu.be/FX3N0LiOwOs&t=2054)]
Yeah.

##### **Geohot** [[00:34:15](https://youtu.be/FX3N0LiOwOs&t=2055)]
Any good? I thought Triton was pretty bad for AMD.

##### **Qazalin** [[00:34:19](https://youtu.be/FX3N0LiOwOs&t=2059)]
I mean, like they handwrite everything, right? So it's either Triton or handwritten HIP kernels. Yeah, it'll be interesting. It'll be interesting. 69 kernels, 3,000 launches. So I think it's manageable by humans.

##### **Geohot** [[00:34:37](https://youtu.be/FX3N0LiOwOs&t=2077)]
The best thing we can get out of this whole project is just a complete understanding of the full taxonomy of the tricks. So this is what I did originally. The original tinygrad project was to replace SNPE for Comma, and I did exactly this. I went through each one of the kernels and said, okay, how do I make our codegen match this? And this is how we ended up with all the image hacks that are now mostly removed but still kind of exist. So, yeah, I mean, that's kind of the goal of the project here, to eventually say, okay, why isn't tinygrad generating the thing? Oh, also, I'm speaking at the AMD's thing in July, so it would be great if by then we have a time that's maybe like 20% better than theirs.

##### **Qazalin** [[00:35:30](https://youtu.be/FX3N0LiOwOs&t=2130)]
Ambitious.

##### **Geohot** [[00:35:31](https://youtu.be/FX3N0LiOwOs&t=2131)]
Doesn't really matter how we do it. But, yeah, if we have some kind of time that's better than theirs, I think that'd be a cool thing to show off.

##### **Qazalin** [[00:35:40](https://youtu.be/FX3N0LiOwOs&t=2140)]
I mean, I was thinking about today, like how much money AMD spent on getting their MLPerf 8B to train, and if we can get all their tricks out of their run.

##### **Geohot** [[00:35:52](https://youtu.be/FX3N0LiOwOs&t=2152)]
Probably not that much money on explicitly that. Right? I don't know. What is their runner written in?

##### **Qazalin** [[00:36:01](https://youtu.be/FX3N0LiOwOs&t=2161)]
Transformer Engine.

##### **Geohot** [[00:36:04](https://youtu.be/FX3N0LiOwOs&t=2164)]
It's some custom AMD shit.

##### **Qazalin** [[00:36:08](https://youtu.be/FX3N0LiOwOs&t=2168)]
It's custom. Actually, it's NVIDIA. And then AMD forked it. And you have like cherry-pick a commit for AMD.

##### **Geohot** [[00:36:17](https://youtu.be/FX3N0LiOwOs&t=2177)]
I see. Wow, I've never even like seen this.

##### **Qazalin** [[00:36:22](https://youtu.be/FX3N0LiOwOs&t=2182)]
Yeah. Is this what it is? It's complicated. Yeah.

##### **Geohot** [[00:36:28](https://youtu.be/FX3N0LiOwOs&t=2188)]
Let's see. I don't know. I don't know.

##### **Qazalin** [[00:36:31](https://youtu.be/FX3N0LiOwOs&t=2191)]
I don't know.

##### **Geohot** [[00:36:32](https://youtu.be/FX3N0LiOwOs&t=2192)]
This looks awful. Yeah. I mean, this looks like the kind of code that you get.

##### **Geohot** [[00:36:43](https://youtu.be/FX3N0LiOwOs&t=2203)]
Before frameworks really start to exist, you always get kind of code that looks like this. Like this has happened in everything that eventually became a framework. Right? Even when you go back to like, I wrote a framework back in the day for RNNs. That was like based on Theano. It was like, RNN additions to Theano. But then like, you know, once we had like torch and stuff that it was, of course, meaningless. So yeah, I have an idea that like things like transformer engine will continue to exist for maybe two or three more years.

##### **Geohot** [[00:37:14](https://youtu.be/FX3N0LiOwOs&t=2234)]
And then some frameworks can be able to just do this better.

##### **Qazalin** [[00:37:22](https://youtu.be/FX3N0LiOwOs&t=2242)]
I'm going to answer why tinygrad can't do the stuff that those can do for now.

##### **Geohot** [[00:37:30](https://youtu.be/FX3N0LiOwOs&t=2250)]
Sounds good.

##### **Qazalin** [[00:37:31](https://youtu.be/FX3N0LiOwOs&t=2251)]
I have answers for the remaining two kernels, two C kernels that aren't in UOps. They need codegen improvements. I thought about it a little bit. They basically need to support built-in max instructions and built-in reciprocal on AMD.

##### **Geohot** [[00:37:53](https://youtu.be/FX3N0LiOwOs&t=2273)]
Yeah,

##### **Geohot** [[00:37:54](https://youtu.be/FX3N0LiOwOs&t=2274)]
I think let me do this. This this sprint. I'll finish up the. The refactor to the new the new spec and then I think I'll hand it off to you to actually implement those things.

##### **Qazalin** [[00:38:07](https://youtu.be/FX3N0LiOwOs&t=2287)]
Yeah,

##### **Geohot** [[00:38:09](https://youtu.be/FX3N0LiOwOs&t=2289)]
I mean like is the problem with the max thing that like we're not supporting the built-in or is the problem that we're not using the max op?

##### **Qazalin** [[00:38:18](https://youtu.be/FX3N0LiOwOs&t=2298)]
Well, you have to use the max op in order to get the max instruction lowered because we decompose it to a where. LLVM has no way to optimize it to a condition. Yeah, it's very functional. And that gets very slow. However, it's not that it's always beneficial to use the max instruction. Sometimes you actually want to use a where. You're definitely on an unrolled argmax. But LLVM is actually smart enough that if you use a built-in max, it won't select the V_MAX instruction. It will select a where. But I didn't want to put our... I had the PR to like merge the use of built-in. And then LLVM is smart enough to use a where if it makes sense. But I don't want to do that because that's not the long-term way you want to do this, relying on LLVM to be smart and pick the better version.

##### **Geohot** [[00:39:12](https://youtu.be/FX3N0LiOwOs&t=2352)]
I can't understand. Why is a where ever better than a max?

##### **Qazalin** [[00:39:16](https://youtu.be/FX3N0LiOwOs&t=2356)]
So imagine if you have a running unrolled argmax in a loop. If you have max, max, max, max, max of max of max of max, with respect to that, it's actually more beneficial to have a where and then just update that single register instead of the...

##### **Geohot** [[00:39:40](https://youtu.be/FX3N0LiOwOs&t=2380)]
Oh, for argmax. I see what you're saying. Just because you already have to do the branch for the argmax.

##### **Qazalin** [[00:39:46](https://youtu.be/FX3N0LiOwOs&t=2386)]
Yeah. On the other hand, for the absmax, absolute maximum, that FP8 quantization uses in LLaMA. If you use a where conditional, it gets 10% slower on the MI300. Only 3% slower on the RDNAs, but 10% slower on MI300s.

##### **Geohot** [[00:40:11](https://youtu.be/FX3N0LiOwOs&t=2411)]
Yeah. Let's just document all this stuff, and then eventually we'll figure out what we need to do.

##### **Geohot** [[00:40:18](https://youtu.be/FX3N0LiOwOs&t=2418)]
Yeah, we'll do that. OK.

##### **Qazalin** [[00:40:22](https://youtu.be/FX3N0LiOwOs&t=2422)]
Codegen fundamental change. For instruction selection.

##### **Geohot** [[00:40:27](https://youtu.be/FX3N0LiOwOs&t=2427)]
Yeah, yeah. Just keep track of all these things in a big list somewhere. And then, yeah, once that list is like, OK, these are all the tricks we're going to need, we should go through them and say, OK, this one's going to go here, this one's going to go here, this belongs here, so on and so forth.

##### **Qazalin** [[00:40:44](https://youtu.be/FX3N0LiOwOs&t=2444)]
Makes sense. Yeah, that's all for me.

##### **Geohot** [[00:40:50](https://youtu.be/FX3N0LiOwOs&t=2450)]
Next MLPerf LLaMA. Very simple here. Can I hear you? Hello? Hello? Okay.

##### **Geohot** [[00:41:27](https://youtu.be/FX3N0LiOwOs&t=2487)]
Let's do HCQ2 first.

##### **Nimlgen** [[00:41:35](https://youtu.be/FX3N0LiOwOs&t=2495)]
So, yeah, I've been working on HCQ2. I've rewritten it, so it basically works over the whole schedule now as a single pass. It also has no multi, and I've completed the dependency tracker, which is the same implementation that we had in Graph, in `HCQ2Graph`, but now it's over the schedule. So, actually, `HCQ2Graph` is no op. Will be no more.

##### **Wozeparrot** [[00:42:11](https://youtu.be/FX3N0LiOwOs&t=2531)]
So, let me try this. `HCQ2=1`?

##### **Geohot** [[00:42:15](https://youtu.be/FX3N0LiOwOs&t=2535)]
Yeah. No module named extra. Feels like the import is slower. I don't know why.

##### **Geohot** [[00:42:27](https://youtu.be/FX3N0LiOwOs&t=2547)]
Okay, cool, yeah. So, I see the number of things that I expect.

##### **Geohot** [[00:42:33](https://youtu.be/FX3N0LiOwOs&t=2553)]
That's good. So, are these things all happening inside the calls? Oh, this is slow. Let me try a simpler one.

##### **Geohot** [[00:43:00](https://youtu.be/FX3N0LiOwOs&t=2580)]
But, okay, yeah, so that makes sense. So, first it's going to do codegen of all the things.

##### **Geohot** [[00:43:04](https://youtu.be/FX3N0LiOwOs&t=2584)]
Then... I don't see anything changing. I'm scrolling down through all the steps, and it doesn't seem like it's changing the graph.

##### **Nimlgen** [[00:43:28](https://youtu.be/FX3N0LiOwOs&t=2608)]
Yeah, I believe that's the VIZ bug or something.

##### **Geohot** [[00:43:33](https://youtu.be/FX3N0LiOwOs&t=2613)]
There's a VIZ bug?

##### **Nimlgen** [[00:43:35](https://youtu.be/FX3N0LiOwOs&t=2615)]
I believe so, yeah, because if you just... You can see the patches. I mean, I know, I'll take a look into this.

##### **Geohot** [[00:43:46](https://youtu.be/FX3N0LiOwOs&t=2626)]
Hmm. Hmm. Yeah, I mean, I just, I see, like, so I'm scrolling down through the, uh... Like, HCQ Schedule Kernels. And... I don't actually see anything changing on any of these.

##### **Nimlgen** [[00:44:03](https://youtu.be/FX3N0LiOwOs&t=2643)]
Yeah, oh, yeah, it's happening inside calls.

##### **Geohot** [[00:44:08](https://youtu.be/FX3N0LiOwOs&t=2648)]
No, even inside the calls, I don't see it. Oh, yeah. Um... Let me see. Do you run with AMD? Uh, no.

##### **Nimlgen** [[00:44:24](https://youtu.be/FX3N0LiOwOs&t=2664)]
Yeah, I haven't fixed that. Actually, that's not a fix, it's just... `ops_amd2` is AMD only.

##### **Geohot** [[00:44:32](https://youtu.be/FX3N0LiOwOs&t=2672)]
Oh, it's AMD only? Yeah. Uh, why is it AMD only? Uh... There's no reason for that, but...

##### **Nimlgen** [[00:44:52](https://youtu.be/FX3N0LiOwOs&t=2692)]
I've been rewriting it, and I just deleted all these... KFD things.

##### **Geohot** [[00:44:58](https://youtu.be/FX3N0LiOwOs&t=2698)]
We see it on AMD. Okay, yeah, okay, on AMD I see the whole stuff. On AMD I see the changes. Cool. Um... What is bind doing here? So, on the call...

##### **Nimlgen** [[00:45:24](https://youtu.be/FX3N0LiOwOs&t=2724)]
Yeah, actually, just to keep the references to the buffers. I know that's not the final, but I need to keep these buffers alive. They are not part of the call. Like, it's the AMD buffers. And it's rewritten to the C kernel. Okay.

##### **Geohot** [[00:45:44](https://youtu.be/FX3N0LiOwOs&t=2744)]
Uh... Oh, so by the AMD buffers you mean like the... ...like, thing that holds the bytes. Yeah.

##### **Nimlgen** [[00:45:52](https://youtu.be/FX3N0LiOwOs&t=2752)]
Yeah, command buffers and also like the inputs.

##### **Geohot** [[00:45:56](https://youtu.be/FX3N0LiOwOs&t=2756)]
Got it. Um... That's a lot of buffers.

##### **Qazalin** [[00:46:11](https://youtu.be/FX3N0LiOwOs&t=2771)]
All right.

##### **Geohot** [[00:46:12](https://youtu.be/FX3N0LiOwOs&t=2772)]
Uh... Like... What are these...

##### **Geohot** [[00:46:22](https://youtu.be/FX3N0LiOwOs&t=2782)]
Oh, okay, so these barriers are... You're using barrier to represent the global...

##### **Geohot** [[00:46:30](https://youtu.be/FX3N0LiOwOs&t=2790)]
...barrier.

##### **Qazalin** [[00:46:32](https://youtu.be/FX3N0LiOwOs&t=2792)]
Yeah.

##### **Geohot** [[00:46:36](https://youtu.be/FX3N0LiOwOs&t=2796)]
It's probably not rendered in C right now, but... Oh. What do you mean in C?

##### **Nimlgen** [[00:46:44](https://youtu.be/FX3N0LiOwOs&t=2804)]
This one is like the... No, no, no. This one is... Like the memory barrier on the queue, which just flushes HCQ.

##### **Geohot** [[00:46:57](https://youtu.be/FX3N0LiOwOs&t=2817)]
Uh, I see. Okay. And then you're putting a LINEAR there. Okay. I see. You're adding the...

##### **Geohot** [[00:47:04](https://youtu.be/FX3N0LiOwOs&t=2824)]
I see weights being added. A weight has a buffer and then an add? Yeah. I mean, we...

##### **Nimlgen** [[00:47:19](https://youtu.be/FX3N0LiOwOs&t=2839)]
So actually we have like... Yeah, it has buffer because these values are... I mean, we have timeline signals and timeline values, and both of these are buffered. So basically when we send... So it's CQ and also it just reads the timeline value, so it just updates all the signals inside the queue as patches, and then writes back to this timeline value. So that's kind of... It's buffer because it's kind of shared between like Python and C programs and whatever.

##### **Geohot** [[00:47:55](https://youtu.be/FX3N0LiOwOs&t=2875)]
Got it. Okay. So I'm looking here at the generated C code. Okay. And I see a very large... At 1844... Is that an address?

##### **Nimlgen** [[00:48:12](https://youtu.be/FX3N0LiOwOs&t=2892)]
No, that's minus one.

##### **Wozeparrot** [[00:48:15](https://youtu.be/FX3N0LiOwOs&t=2895)]
Oh, that's minus one.

##### **Geohot** [[00:48:17](https://youtu.be/FX3N0LiOwOs&t=2897)]
Yeah. Okay. We should improve the rendering of that. That's okay.

##### **Geohot** [[00:48:33](https://youtu.be/FX3N0LiOwOs&t=2913)]
Totally separate issue. All right, cool. Then that becomes... Why is there like a weird enter in between the...

##### **Nimlgen** [[00:48:44](https://youtu.be/FX3N0LiOwOs&t=2924)]
That's the barrier. It's not rendered, but I think we should have like the memory barrier with some specific to the architecture if it's ARM. So that's like visible before the doorbell on the GPU.

##### **Geohot** [[00:49:04](https://youtu.be/FX3N0LiOwOs&t=2944)]
Oh, I see. Okay. So I mean, that's very different from like what a GPU barrier is. That's more like a fence. Yeah.

##### **Nimlgen** [[00:49:13](https://youtu.be/FX3N0LiOwOs&t=2953)]
Yeah.

##### **Wozeparrot** [[00:49:13](https://youtu.be/FX3N0LiOwOs&t=2953)]
Yeah. Okay.

##### **Geohot** [[00:49:16](https://youtu.be/FX3N0LiOwOs&t=2956)]
So what are these 85 things that it's doing?

##### **Nimlgen** [[00:49:22](https://youtu.be/FX3N0LiOwOs&t=2962)]
85 is the queue command buffer size. So it's basically... Well, zero is the... Yeah. I think that's the first thing. And then it's the doorbell. Like the next doorbell. And it just strings updates all these write pointers and the... Before and after this page, that's the doorbell.

##### **Geohot** [[00:49:42](https://youtu.be/FX3N0LiOwOs&t=2982)]
Oh, I see. Okay. So this is like you have basically a mem copy, and then you have... The doorbell is the final thing, the last thing that's written down.

##### **Nimlgen** [[00:49:55](https://youtu.be/FX3N0LiOwOs&t=2995)]
Yeah. It's data one. It's the doorbell. Data zero is the... Yeah. And then it's like the new timeline value.

##### **Geohot** [[00:50:01](https://youtu.be/FX3N0LiOwOs&t=3001)]
I mean, it'd be nice to support names for buffers, but... You know, names for buffers now have the problem of... Let's name two different things in two different places. Yeah. Okay. Then HCQ submit actually runs these. Let's see how it looks in the profiler. Cool. I mean, yeah, this is great. It's still going to take... I still see a lot of work to be done on this, but I mean, hopefully this framework basically feels correct.

##### **Geohot** [[00:50:45](https://youtu.be/FX3N0LiOwOs&t=3045)]
And then are these programs rerunnable?

##### **Wozeparrot** [[00:50:50](https://youtu.be/FX3N0LiOwOs&t=3050)]
Yeah.

##### **Geohot** [[00:50:52](https://youtu.be/FX3N0LiOwOs&t=3052)]
So actually, that's why the...

##### **Nimlgen** [[00:50:55](https://youtu.be/FX3N0LiOwOs&t=3055)]
Sure. What do you mean by rerunnable?

##### **Geohot** [[00:50:58](https://youtu.be/FX3N0LiOwOs&t=3058)]
If I want to run... Yeah. So basically, every time I run the same graph, I don't want to have to regenerate the program.

##### **Nimlgen** [[00:51:09](https://youtu.be/FX3N0LiOwOs&t=3069)]
Yeah, yeah, yeah. Definitely. Yeah. So that's why I have timeline values here.

##### **Geohot** [[00:51:15](https://youtu.be/FX3N0LiOwOs&t=3075)]
Yeah. So the timeline values are passed in as integers or no?

##### **Nimlgen** [[00:51:19](https://youtu.be/FX3N0LiOwOs&t=3079)]
No. They're like the buffer. So it's just the data zero... No, it's actually... They're not the dup. But actually, the data zero just updates the timeline value, and one of the data fields just rereads the old timeline value. So basically, you can resubmit it and you'll be fine.

##### **Geohot** [[00:51:45](https://youtu.be/FX3N0LiOwOs&t=3105)]
I don't see any wait.

##### **Geohot** [[00:51:50](https://youtu.be/FX3N0LiOwOs&t=3110)]
Wait, you run, which is like the second line. Oh. Well, I see a store, but I don't see like a... I don't see like a wait anywhere. Yeah.

##### **Nimlgen** [[00:52:08](https://youtu.be/FX3N0LiOwOs&t=3128)]
So yeah, I know that, yeah, there is no wait. And I don't know if we need this. We just need wait, actually, just to be sure that we do not overflow the command... Like the GPU ring. Only for that.

##### **Geohot** [[00:52:28](https://youtu.be/FX3N0LiOwOs&t=3148)]
I see. But the wait right now is still basically the same as the wait for the GPU. Yeah. So basically implemented in Python.

##### **Geohot** [[00:52:34](https://youtu.be/FX3N0LiOwOs&t=3154)]
Yeah. That's probably fine.

##### **Wozeparrot** [[00:52:37](https://youtu.be/FX3N0LiOwOs&t=3157)]
It might be fine.

##### **Geohot** [[00:52:39](https://youtu.be/FX3N0LiOwOs&t=3159)]
We just have large enough queues. Yeah, keep it up. Do you have a clear direction on this or anything you want, like any like stuff you're struggling

##### **Geohot** [[00:52:53](https://youtu.be/FX3N0LiOwOs&t=3173)]
with?

##### **Nimlgen** [[00:52:55](https://youtu.be/FX3N0LiOwOs&t=3175)]
No, I think next I'm going to refactor the... Oh, I see. Like the way all these like queues... So I don't know. I think I want to use instructions and like add separate stages. Like currently we just have like LINEAR and after that we just immediately got the blob. But probably I can add more readable stages in between. So that's... Currently you're having... LINEAR and...

##### **Geohot** [[00:53:31](https://youtu.be/FX3N0LiOwOs&t=3211)]
Sorry, I didn't follow that.

##### **Nimlgen** [[00:53:32](https://youtu.be/FX3N0LiOwOs&t=3212)]
Yeah. And when we have like... So I mean we have like encode... I don't remember like `amd: encode` or something like that. It just takes the LINEAR of the like so-called HCQ IR UOps and just produces blob immediately.

##### **Geohot** [[00:53:50](https://youtu.be/FX3N0LiOwOs&t=3230)]
Oh, I see. Yeah.

##### **Nimlgen** [[00:53:52](https://youtu.be/FX3N0LiOwOs&t=3232)]
Yeah. And I think maybe I can just add several stages with instructions. Kind of. Yeah. Yeah. Yeah. We have some kind of... Instructions. Yeah.

##### **Geohot** [[00:54:02](https://youtu.be/FX3N0LiOwOs&t=3242)]
We have an instruction set for the MEC. Sure. Yeah. And that's the way I think about it.

##### **Qazalin** [[00:54:07](https://youtu.be/FX3N0LiOwOs&t=3247)]
Cool.

##### **Geohot** [[00:54:08](https://youtu.be/FX3N0LiOwOs&t=3248)]
Yeah. I mean, it's crazy. Like it gets all like so confusing to start to think about like, yeah, you have all these different processors with all these different instruction sets and they all kind of do different things, but they all kind of follow these same basic ideas, right? Like the MEC is just a computer. It's a thing with a weird instruction set. Yeah. Yeah. It's just a thing that's like, you know, definitely when we build our own hardware, I'm not going to have a MEC, I'm going to have a RISC-V core. And you'll just generate some RISC-V code, you'll just like, like, why is the MEC a thing? Like, why is it parsing this weird command buffer format when you could just put a RISC-V core on there? I don't... Did you see what I mean?

##### **Geohot** [[00:54:51](https://youtu.be/FX3N0LiOwOs&t=3291)]
Yeah. Yeah.

##### **Qazalin** [[00:54:55](https://youtu.be/FX3N0LiOwOs&t=3295)]
Cool. Cool.

##### **Geohot** [[00:55:00](https://youtu.be/FX3N0LiOwOs&t=3300)]
Does my mic work? Yes.

##### **Wozeparrot** [[00:55:05](https://youtu.be/FX3N0LiOwOs&t=3305)]
So 70B trains, it is really slow. I have a run going right now.

##### **Geohot** [[00:55:12](https://youtu.be/FX3N0LiOwOs&t=3312)]
Post the link. I feel like we already had a run for this and it was also slow.

##### **Wozeparrot** [[00:55:19](https://youtu.be/FX3N0LiOwOs&t=3319)]
We had an 8B MP run. So I had a completed 8B MP run.

##### **Geohot** [[00:55:27](https://youtu.be/FX3N0LiOwOs&t=3327)]
Okay. How long did that take?

##### **Wozeparrot** [[00:55:29](https://youtu.be/FX3N0LiOwOs&t=3329)]
That took 25 hours.

##### **Geohot** [[00:55:32](https://youtu.be/FX3N0LiOwOs&t=3332)]
Yeah, something's wrong.

##### **Geohot** [[00:55:35](https://youtu.be/FX3N0LiOwOs&t=3335)]
Where's the 70B run?

##### **Wozeparrot** [[00:55:42](https://youtu.be/FX3N0LiOwOs&t=3342)]
So 70B, we spent 50 seconds in optim.

##### **Geohot** [[00:55:52](https://youtu.be/FX3N0LiOwOs&t=3352)]
On the CPU or? On the CPU. We're getting an MFU of 3.3. That's one third of an xAI. How long do we expect this to take?

##### **Wozeparrot** [[00:56:17](https://youtu.be/FX3N0LiOwOs&t=3377)]
This should converge in about the same steps as 8B. It's the 8B training recipe, but with 70B instead.

##### **Geohot** [[00:56:29](https://youtu.be/FX3N0LiOwOs&t=3389)]
You do grad accumulation? So this should be, yeah. 32 steps.

##### **Qazalin** [[00:56:36](https://youtu.be/FX3N0LiOwOs&t=3396)]
Okay.

##### **Chenyu** [[00:56:39](https://youtu.be/FX3N0LiOwOs&t=3399)]
So it's more than half of the time is optim even with grad accumulation?

##### **Wozeparrot** [[00:56:45](https://youtu.be/FX3N0LiOwOs&t=3405)]
Yes. The 8B recipe doesn't do as much grad accumulation as the 405B recipe.

##### **Geohot** [[00:56:55](https://youtu.be/FX3N0LiOwOs&t=3415)]
405B does order of magnitude more.

##### **Wozeparrot** [[00:57:00](https://youtu.be/FX3N0LiOwOs&t=3420)]
Grad accumulation. But optim also takes longer on 405B.

##### **Geohot** [[00:57:06](https://youtu.be/FX3N0LiOwOs&t=3426)]
But why is optim so slow? Is it like bad CPU codegen or?

##### **Wozeparrot** [[00:57:12](https://youtu.be/FX3N0LiOwOs&t=3432)]
Optim does a lot now. Because optim also has to do the quantize to FP8, which requires a reduce to get the AMAX. And we're trying to do that on the... We can't fit the optim on the GPU, but I think what we can do is we can just keep, we can potentially keep M and V just stored on the CPU and then transfer to the GPU to do compute.

##### **Geohot** [[00:57:48](https://youtu.be/FX3N0LiOwOs&t=3468)]
I see. And that will also work for 405B?

##### **Wozeparrot** [[00:57:57](https://youtu.be/FX3N0LiOwOs&t=3477)]
Yes.

##### **Geohot** [[00:58:03](https://youtu.be/FX3N0LiOwOs&t=3483)]
Just do more copies.

##### **Wozeparrot** [[00:58:10](https://youtu.be/FX3N0LiOwOs&t=3490)]
Right now my problem with 405B is we're still not fitting on CPU memory.

##### **Geohot** [[00:58:17](https://youtu.be/FX3N0LiOwOs&t=3497)]
Why not?

##### **Wozeparrot** [[00:58:23](https://youtu.be/FX3N0LiOwOs&t=3503)]
Something stochastic rounding related where we have to keep an FP... It's FP8 quantize keeps the FP32 buffer around.

##### **Geohot** [[00:58:37](https://youtu.be/FX3N0LiOwOs&t=3517)]
I see. And then M and V are 32 or 16?

##### **Wozeparrot** [[00:58:44](https://youtu.be/FX3N0LiOwOs&t=3524)]
16.

##### **Geohot** [[00:58:46](https://youtu.be/FX3N0LiOwOs&t=3526)]
Should fit. M and V are 16.

##### **Wozeparrot** [[00:58:49](https://youtu.be/FX3N0LiOwOs&t=3529)]
So they barely fits. Yeah.

##### **Geohot** [[00:58:52](https://youtu.be/FX3N0LiOwOs&t=3532)]
So we have like three terabytes of RAM, right? So M and V are going to be like 1.6 terabytes.

##### **Wozeparrot** [[00:58:57](https://youtu.be/FX3N0LiOwOs&t=3537)]
Yeah. And then you also have intermediates and the grads.

##### **Geohot** [[00:59:03](https://youtu.be/FX3N0LiOwOs&t=3543)]
What intermediates?

##### **Wozeparrot** [[00:59:05](https://youtu.be/FX3N0LiOwOs&t=3545)]
Any compute intermediates plus grads.

##### **Geohot** [[00:59:08](https://youtu.be/FX3N0LiOwOs&t=3548)]
Compute intermediates can be small. Grads are FP8.

##### **Geohot** [[00:59:13](https://youtu.be/FX3N0LiOwOs&t=3553)]
BF16. Why are grads in FP8?

##### **Wozeparrot** [[00:59:20](https://youtu.be/FX3N0LiOwOs&t=3560)]
Uh, FP8 grads don't train. It doesn't converge.

##### **Geohot** [[00:59:25](https://youtu.be/FX3N0LiOwOs&t=3565)]
Doesn't converge. Okay. The grads are BF16. Okay. So we can fit basically, we can fit basically three buffers on the CPU.

##### **Geohot** [[00:59:35](https://youtu.be/FX3N0LiOwOs&t=3575)]
Yeah. Um, yeah. Okay. And then model parallel.

##### **Geohot** [[00:59:44](https://youtu.be/FX3N0LiOwOs&t=3584)]
Yeah. I don't know. I mean, we should just, uh, like benchmark these things and figure out like, are we not?

##### **Geohot** [[00:59:50](https://youtu.be/FX3N0LiOwOs&t=3590)]
It's expected. It's expected to be this low or.

##### **Wozeparrot** [[00:59:56](https://youtu.be/FX3N0LiOwOs&t=3596)]
It's unclear if it's expected to be this slow. There's like not really a good reference to go off of.

##### **Geohot** [[01:00:06](https://youtu.be/FX3N0LiOwOs&t=3606)]
And like, are we going to need a set of master weights?

##### **Wozeparrot** [[01:00:10](https://youtu.be/FX3N0LiOwOs&t=3610)]
And that's also not that clear right now. I still have to do more testing with stochastic rounding to see if stochastic rounding actually converges on bigger models. I see. So you think with stochastic rounding, we might not need the master weights? Well, with stochastic rounding, stochastic rounding will replace master weights and then we won't have master weights at all.

##### **Geohot** [[01:00:36](https://youtu.be/FX3N0LiOwOs&t=3636)]
I see.

##### **Wozeparrot** [[01:00:37](https://youtu.be/FX3N0LiOwOs&t=3637)]
It's unclear if stochastic rounding has the same convergence as without stochastic rounding. The weights are FP8? Weights are FP8. Yeah. But weights are on GPU.

##### **Qazalin** [[01:00:50](https://youtu.be/FX3N0LiOwOs&t=3650)]
Yeah.

##### **Geohot** [[01:00:51](https://youtu.be/FX3N0LiOwOs&t=3651)]
Yeah. Well, yeah, but you got to copy them. I guess you don't have to copy them. You just copy the weight update to the GPU.

##### **Wozeparrot** [[01:00:59](https://youtu.be/FX3N0LiOwOs&t=3659)]
Yeah.

##### **Qazalin** [[01:01:01](https://youtu.be/FX3N0LiOwOs&t=3661)]
Yeah.

##### **Geohot** [[01:01:04](https://youtu.be/FX3N0LiOwOs&t=3664)]
Okay. So then if we're, what's the, so there's, with the current step time for 70B, when do we expect this to converge?

##### **Geohot** [[01:01:18](https://youtu.be/FX3N0LiOwOs&t=3678)]
70B.

##### **Qazalin** [[01:01:19](https://youtu.be/FX3N0LiOwOs&t=3679)]
Yeah.

##### **Geohot** [[01:01:26](https://youtu.be/FX3N0LiOwOs&t=3686)]
When do you expect it? This week? This week. Yeah. Yeah.

##### **Geohot** [[01:01:38](https://youtu.be/FX3N0LiOwOs&t=3698)]
I mean, can we set, can we, with 70B, can we set the grad accumulate, like the batch size to be the same as 405?

##### **Wozeparrot** [[01:01:48](https://youtu.be/FX3N0LiOwOs&t=3708)]
Yeah.

##### **Geohot** [[01:01:50](https://youtu.be/FX3N0LiOwOs&t=3710)]
Yeah. Let's do that. Let's do that. So we're doing the correct amount of

##### **Wozeparrot** [[01:01:53](https://youtu.be/FX3N0LiOwOs&t=3713)]
steps for... I can just switch to the other, the 405B recipe. That's for fine-tuning, not for retrain. Not... yeah.

##### **Geohot** [[01:02:04](https://youtu.be/FX3N0LiOwOs&t=3724)]
Still, yeah, we should do that. We should make the 70B the same as the 405B. Yeah, okay. So we know what we actually have to optimize. Yeah, let's go through these things and post, like, a... figure out, like, okay, where actually is the bottleneck? You know, if it's taking 50 seconds, is it taking 50 seconds because that's expected with the PCIe bandwidth, or is it taking 50 seconds because you know, we just have some slow thing?

##### **Nimlgen** [[01:02:27](https://youtu.be/FX3N0LiOwOs&t=3747)]
Yeah.

##### **Wozeparrot** [[01:02:29](https://youtu.be/FX3N0LiOwOs&t=3749)]
And then MLPerf-wise, our reviews are done. We're good there. No one had any complaints. They wanted us to do a precision thing. Apparently they merged this, like, last minute. And then no one did it. So now they're telling people to retroactively do it?

##### **Geohot** [[01:02:51](https://youtu.be/FX3N0LiOwOs&t=3771)]
No, don't do it. What is it? What's a precision thing? Your mic might break again. Okay.

##### **Qazalin** [[01:03:19](https://youtu.be/FX3N0LiOwOs&t=3799)]
Okay.

##### **Chenyu** [[01:03:22](https://youtu.be/FX3N0LiOwOs&t=3802)]
You can post the whatever updates in the MLPerf channel. Yeah, I want to know what they are. Especially if there's any action items left to be aware of.

##### **Geohot** [[01:03:41](https://youtu.be/FX3N0LiOwOs&t=3821)]
Anything else from Comma?

##### **Chenyu** [[01:03:43](https://youtu.be/FX3N0LiOwOs&t=3823)]
Is Comma happy?

##### **Geohot** [[01:03:46](https://youtu.be/FX3N0LiOwOs&t=3826)]
I think so. Yeah. Yeah, I think they're running eGPUs.

##### **Wozeparrot** [[01:03:49](https://youtu.be/FX3N0LiOwOs&t=3829)]
Any complaints?

##### **Geohot** [[01:03:52](https://youtu.be/FX3N0LiOwOs&t=3832)]
I don't know. I don't know.

##### **Chrism** [[01:03:53](https://youtu.be/FX3N0LiOwOs&t=3833)]
I don't know. People are running GPUs. So maybe we'll have complaints, but.

##### **Geohot** [[01:04:00](https://youtu.be/FX3N0LiOwOs&t=3840)]
I don't see updates for assembly.

##### **Chenyu** [[01:04:04](https://youtu.be/FX3N0LiOwOs&t=3844)]
Is that still a thing?

##### **Geohot** [[01:04:08](https://youtu.be/FX3N0LiOwOs&t=3848)]
I mean, I think so. I don't know. I gave him that thing for the RDNA3. We'll see if he does it. Yeah, no, I didn't take assembly out. It's like fine. I mean, I just have to do that, you know, with all the stuff I got to do the cleanup work, but. It's mostly fine. And like, I'm kind of thinking of how to rewrite the C-style renderer in terms of something that looks more like instruction selection. Like there's no register allocation, but, you know, there's no register allocation like LLVM, PTX don't have register allocation either. The only thing that the only real difference between assembly and like LLVM, PTX is that, yeah, there is no, there's no, are no, no register allocation. They still have instruction selection. So write something that looks

##### **Geohot** [[01:04:55](https://youtu.be/FX3N0LiOwOs&t=3895)]
like that.

##### **Wozeparrot** [[01:04:58](https://youtu.be/FX3N0LiOwOs&t=3898)]
Okay, anything else for the meeting? I think that's about it.

##### **Geohot** [[01:05:08](https://youtu.be/FX3N0LiOwOs&t=3908)]
Wozeparrot, if you fix your mic, what was the precision thing?

##### **Wozeparrot** [[01:05:13](https://youtu.be/FX3N0LiOwOs&t=3913)]
Does it work now?

##### **Geohot** [[01:05:14](https://youtu.be/FX3N0LiOwOs&t=3914)]
Yes.

##### **Wozeparrot** [[01:05:15](https://youtu.be/FX3N0LiOwOs&t=3915)]
I just switched to web Discord.

##### **Geohot** [[01:05:18](https://youtu.be/FX3N0LiOwOs&t=3918)]
I had to switch to web Discord; desktop Discord for some reason had to stop. Okay. Disconnecting.

##### **Wozeparrot** [[01:05:25](https://youtu.be/FX3N0LiOwOs&t=3925)]
They added a precision thing. Apparently it was required for this round, but they added it like right before the logging stuff, right before results were

##### **Chenyu** [[01:05:36](https://youtu.be/FX3N0LiOwOs&t=3936)]
supposed to be due.

##### **Wozeparrot** [[01:05:38](https://youtu.be/FX3N0LiOwOs&t=3938)]
So no one has the precision stuff in their logs. They've been telling people to retroactively... Oh, I just added it to our logs. Good now.

##### **Geohot** [[01:05:47](https://youtu.be/FX3N0LiOwOs&t=3947)]
Oh, okay, great. We did that. Great. But it's unclear if this will even affect the final result. Unclear if it'll what? Late, right. Yeah. No, I mean, I just want to make sure that there's nothing wrong with our submission and it gets on the board. Yeah, no, we're good. Okay, great.

##### **Chenyu** [[01:06:13](https://youtu.be/FX3N0LiOwOs&t=3973)]
Well, sounds good. Okay. I think that's it for the meeting. Thank you, everyone. See you next week. Bye bye.

##### **Geohot** [[01:06:21](https://youtu.be/FX3N0LiOwOs&t=3981)]
Thank you. Bye.
