# 2026-06-22 Meeting

### Meeting Agenda

**Time:** new meeting #25, 6/22 9am Monday San Diego time
- company update
- hcq2
- CI updates
- llama training
- VIZ llama schedule
- const mixin
- IR refactor
- bounties, issues, comma happiness, GLM


### Audio

[Youtube Link](https://www.youtube.com/watch?v=N06R1rFVQpA)

### Highlights

- **[Company Update](#geohot-000006)**: Tinygrad sold an Exabox pre-order and now needs to coordinate GPU choice and deployment details; Tinybox Green V2 sales were also strong for the week.

- **[GLM Runner](#geohot-000042)**: Geohot has been using GLM for three days and says it feels as good as other models in practice, while also being faster; the goal is to eventually run it at around 500 tokens/sec.

- **[HCQ2 Status](#nimlgen-000144)**: HCQ2 has all major features working, with profiling as the last piece; Nimlgen plans to merge it and then rewrite/clean up the implementation while moving backends over iteratively.

- **[HCQ2 Spec Compliance](#geohot-000442)**: Geohot flags that HCQ2 must match the UOp spec exactly, including using `shrink` + `bitcast` instead of invalid casts on the left-hand side of stores.

- **[HCQ2 Buffer Lifetime Handling](#geohot-001003)**: The current use of `bind` to keep buffers alive violates the spec; Geohot suggests representing those buffers through an `after` node so the call parameters still match correctly.

- **[CI Dashboard and LLM Metrics](#chrism-001233)**: The CI stats page now shows LLM benchmarks near the top, with most using `tinygrad.LLM`, and graph units were fixed to show tokens/sec and seconds.

- **[CI Docker and Dependency Size](#chrism-001415)**: Docker was tested for CI setup but was slower than the current setup path; large dependencies like AMD co-manager and Mesa Vulkan drivers remain a major source of CI size and complexity.

- **[CI Test Reduction](#geohot-001802)**: Geohot suggests checking historical failures to see whether slow macOS/LLVM/Clang tests have caught real issues, and reducing or splitting tests if they have not.

- **[Rusticl/OpenCL Exploration](#chrism-001831)**: Rusticl looks promising as an open-source OpenCL runtime and may be faster than Intel’s runtime on R4, but it still has bugs around FP16 bitcasting and data-dependent loading.

- **[LLaMA Training MXFP8](#wozeparrot-002750)**: MXFP8 convergence issues were fixed; the main bug was in the transpose BF16 GEMM under model parallelism, and MP now converges for both AB and AP cases.

- **[70B Training Path](#geohot-003001)**: Geohot pushes for getting a 70B model converged and asks how to reduce the run time from about a week toward a day; porting DP kernels to MP/MXFP8 is the next optimization path.

- **[VIZ LLaMA Performance](#qazalin-003600)**: The latest VIZ LLaMA run is the fastest yet, around 1.54–1.61 seconds per step versus AMD at roughly 1.3–1.4 seconds, leaving about a 263 ms gap.

- **[E-Kernel Removal](#qazalin-003654)**: Qazalin’s main path to matching AMD is removing extra E-kernels; the branch is already down to about 5,900 kernels, with speedups coming from eliminating unnecessary launches.

- **[Const and Training Context](#chenyu-004421)**: Chenyu finished the invalid const/clone work so consts now have empty/null sources, and plans to replace `Tensor.training` / `Tensor.train` behavior with a context variable.

- **[IR Refactor and dtype.vec Removal](#geohot-005133)**: Geohot removed `vec` from render boundaries, is replacing `DefineLocal`, `DefineReg`, and `DefineVar` with `buffer` and `param`, and aims to stop creating `dtype.vec` anywhere in the codegen path.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=N06R1rFVQpA&t=0)]
Okay, great. Welcome everyone. Let's get started with company updates.

##### **Geohot** [[00:00:06](https://www.youtube.com/watch?v=N06R1rFVQpA&t=6)]
So yeah, most excitingly, we sold an Exabox. Actually, someone paid the pre-order.

##### **Chenyu** [[00:00:15](https://www.youtube.com/watch?v=N06R1rFVQpA&t=15)]
Now we actually need to build it?

##### **Geohot** [[00:00:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=18)]
Yeah, now we actually need to build it. So I sent an email and asked him, you know, what GPUs does he want? Where is he going to deploy it? And figure all that out. But sales have been great this week. Sold a whole bunch more Tinybox, Green V2s. I think that's kind of, you know, the GLM is very exciting. Like, I actually have just been using GLM for the last three days. It's just as good.

##### **Geohot** [[00:00:51](https://www.youtube.com/watch?v=N06R1rFVQpA&t=51)]
I can't spot where the other models are better, really.

##### **Geohot** [[00:00:58](https://www.youtube.com/watch?v=N06R1rFVQpA&t=58)]
I know they do better in the benchmarks, but I don't know. Also, our GLM is just faster, which is kind of nice. I mean, I really want it to be like really fast. Like that thing running at 500 tokens per second, which is just, you know, it's motivation to actually get Tinygrad like working and get Tinygrad to run at 500 tokens a second.

##### **Chenyu** [[00:01:21](https://www.youtube.com/watch?v=N06R1rFVQpA&t=81)]
Great. Sounds good.

##### **Geohot** [[00:01:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=89)]
Okay, let's move on. I copy the same order. So we'll start with HCQ2.

##### **Chenyu** [[00:01:39](https://www.youtube.com/watch?v=N06R1rFVQpA&t=99)]
Yeah.

##### **Nimlgen** [[00:01:44](https://www.youtube.com/watch?v=N06R1rFVQpA&t=104)]
Basically, I have all features working in HCQ2. The last one is profiling and finishing with this. And I'm going to merge it today. Okay. Okay. Okay. I'm going to rewrite the whole htq2 and put it out of the extra. Maybe as a backend I'll start with nb because actually I want to... I'm kind of familiar with AMD already and how it interacts with the htq2 and QMD stuff is a bit different for nb. I think I'll move nb first to htq2 in master. Especially I think it's not as heavily used as AMD. Yeah, that's for this week.

##### **Geohot** [[00:02:44](https://www.youtube.com/watch?v=N06R1rFVQpA&t=164)]
Yeah, we really want to delete htq1.

##### **Nimlgen** [[00:02:49](https://www.youtube.com/watch?v=N06R1rFVQpA&t=169)]
Yeah, we will, but...

##### **Chenyu** [[00:02:55](https://www.youtube.com/watch?v=N06R1rFVQpA&t=175)]
Yeah, I mean... I think I just will move backhands iteratively.

##### **Geohot** [[00:03:06](https://www.youtube.com/watch?v=N06R1rFVQpA&t=186)]
I'm also looking... So I'm running viz for htq2 now and I see cast being used on...

##### **Geohot** [[00:03:17](https://www.youtube.com/watch?v=N06R1rFVQpA&t=197)]
What does cast do then?

##### **Qazalin** [[00:03:20](https://www.youtube.com/watch?v=N06R1rFVQpA&t=200)]
Yeah.

##### **Chenyu** [[00:03:25](https://www.youtube.com/watch?v=N06R1rFVQpA&t=205)]
I don't know. I don't know. I based it in general.

##### **Nimlgen** [[00:03:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=209)]
Yeah, yeah. So basically we have buffers allocated in the type of HR and basically we just get this address related into the bytes with index and after that we just cast and we store it as integer.

##### **Geohot** [[00:03:52](https://www.youtube.com/watch?v=N06R1rFVQpA&t=232)]
Yeah. So, okay. There's two bugs with that. Yeah. Yeah. And we have to, in general, start being very careful that we comply with the spec.

##### **Chenyu** [[00:04:07](https://www.youtube.com/watch?v=N06R1rFVQpA&t=247)]
Right? So how does that violate the spec? I mean, looks like the cast shouldn't be there.

##### **Geohot** [[00:04:31](https://www.youtube.com/watch?v=N06R1rFVQpA&t=271)]
It's not that the cast shouldn't be there. It's that you want bit cast, right?

##### **Chenyu** [[00:04:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=280)]
Yeah.

##### **Geohot** [[00:04:42](https://www.youtube.com/watch?v=N06R1rFVQpA&t=282)]
You can't cast the left-hand side of a store. And then with bit cast, you also have to be careful because you can't bit cast that indexed Uchar because that indexed Uchar doesn't have the right shape. So what you want instead there is you want to shrink to go from like 268 to 272, and then you want to bit cast it to int, and then you can store there. I think it's really important that before we start moving things to HTQ2, because it just ends up like this is what I'm running into with the AST refactor. It just ends up being a ton of redundant work if you're not like super careful from the beginning to make sure that everything like perfectly matches the spec.

##### **Chenyu** [[00:05:33](https://www.youtube.com/watch?v=N06R1rFVQpA&t=333)]
So that's like param, shrink, bit cast.

##### **Geohot** [[00:05:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=340)]
And I'm not sure bit cast is actually correct with the shapes. If it's not, we should fix it. But yeah, then you can store.

##### **Chenyu** [[00:05:56](https://www.youtube.com/watch?v=N06R1rFVQpA&t=356)]
Makes sense.

##### **Geohot** [[00:06:01](https://www.youtube.com/watch?v=N06R1rFVQpA&t=361)]
Is there anything else like that?

##### **Geohot** [[00:06:04](https://www.youtube.com/watch?v=N06R1rFVQpA&t=364)]
I mean, I know it works. Yeah. We just need to be stricter about checking all this stuff.

##### **Chenyu** [[00:06:19](https://www.youtube.com/watch?v=N06R1rFVQpA&t=379)]
And then how does HTQ2 look for metal? No, I haven't thought a lot about that. I don't know. I'll experiment with metal.

##### **Geohot** [[00:06:48](https://www.youtube.com/watch?v=N06R1rFVQpA&t=408)]
I mean, how do we eventually see this going? Sorry, go ahead.

##### **Nimlgen** [[00:06:55](https://www.youtube.com/watch?v=N06R1rFVQpA&t=415)]
Yeah, I mean, the main problem with HTQ2 and metal that actually HTQ thinks that you can encode like the common queues to bytes. Yeah. Yeah. I think that's not possible. So you just call an API and they do encoding behind the wall.

##### **Geohot** [[00:07:16](https://www.youtube.com/watch?v=N06R1rFVQpA&t=436)]
Yeah, I mean, I wonder if the primary thing here is the idea that like HTQ2 can encode a command queue to bytes, or is the more fundamental thing that HTQ2 can generate C code that executes the command queue?

##### **Geohot** [[00:07:33](https://www.youtube.com/watch?v=N06R1rFVQpA&t=453)]
Yeah.

##### **Nimlgen** [[00:07:45](https://www.youtube.com/watch?v=N06R1rFVQpA&t=465)]
Yeah, that's right. Yeah, that's possible.

##### **Geohot** [[00:07:47](https://www.youtube.com/watch?v=N06R1rFVQpA&t=467)]
Yeah, like you could kind of see, I mean, you could kind of see a world in which like, I don't know, I don't know how much of a break this is in the abstractions. Maybe it's not something we should focus on. But you can see where like the CUDA backend generates CUDA code, right?

##### **Geohot** [[00:08:03](https://www.youtube.com/watch?v=N06R1rFVQpA&t=483)]
Like C code that is CUDA.

##### **Qazalin** [[00:08:10](https://www.youtube.com/watch?v=N06R1rFVQpA&t=490)]
Yeah.

##### **Chenyu** [[00:08:11](https://www.youtube.com/watch?v=N06R1rFVQpA&t=491)]
Yeah. It's a little bit of a Yeah.

##### **Geohot** [[00:08:14](https://www.youtube.com/watch?v=N06R1rFVQpA&t=494)]
Yeah, I think that should be doable.

##### **Nimlgen** [[00:08:15](https://www.youtube.com/watch?v=N06R1rFVQpA&t=495)]
Not much to change to do that.

##### **Geohot** [[00:08:19](https://www.youtube.com/watch?v=N06R1rFVQpA&t=499)]
Yeah, I think that's probably the right idea. Like it's okay to have to compile some C code. Yeah, to use these APIs, but I don't know. That's probably not the place to focus. Just, if anything, it's like, you know, it's a little bit more complicated than that. It's just a way to like, think about making the API a bit more abstract.

##### **Nimlgen** [[00:08:42](https://www.youtube.com/watch?v=N06R1rFVQpA&t=522)]
So yeah, and basically how it works right now, we have like the custom function submit. And behind that, we have linear with like, so-called HTQ IR, which is like the ops of HTQ comments. And basically, these comments can be encoded to C, like C calls or something like that. And these custom functions submit, it's backend dependent. So for like metal CUDA, you can just generate not the submit loop of bytes, but like insert these C strings and call external functions.

##### **Geohot** [[00:09:25](https://www.youtube.com/watch?v=N06R1rFVQpA&t=565)]
Yeah, yeah, yeah. It's like custom. That should work. I also see bind here. What does that do? I mean, that's not how bind is used in the big data.

##### **Nimlgen** [[00:09:37](https://www.youtube.com/watch?v=N06R1rFVQpA&t=577)]
Yeah, so basically that's, maybe we need to new your, but what bind does here is to just store the buffers. I mean, they encoded as addresses into the common buffer and just to hold buffers and just not allow them to be freed until the run linear completes. So like, yeah.

##### **Geohot** [[00:10:03](https://www.youtube.com/watch?v=N06R1rFVQpA&t=603)]
This definitely shouldn't be. Don't be afraid to use new U ops. If you're, if you're using an existing U op, like it should perfectly match the spec.

##### **Geohot** [[00:10:16](https://www.youtube.com/watch?v=N06R1rFVQpA&t=616)]
When I see bind there, I expect to see a variable and a const.

##### **Geohot** [[00:10:24](https://www.youtube.com/watch?v=N06R1rFVQpA&t=624)]
I see what you're doing there. You're just, you're just trying to keep these alive. It's not even a real input to the call.

##### **Geohot** [[00:10:33](https://www.youtube.com/watch?v=N06R1rFVQpA&t=633)]
Does that call have a param of that number? No.

##### **Chenyu** [[00:10:37](https://www.youtube.com/watch?v=N06R1rFVQpA&t=637)]
No.

##### **Geohot** [[00:10:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=640)]
Yeah. I mean, that violates the spec also. See it is nine. Yeah. There's not even, where's eight.

##### **Geohot** [[00:10:54](https://www.youtube.com/watch?v=N06R1rFVQpA&t=654)]
It's a buffer. I mean, the call should never have a number that doesn't match the number of parameters.

##### **Qazalin** [[00:11:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=662)]
Yeah. Yeah. Yeah. Yeah.

##### **Geohot** [[00:11:06](https://www.youtube.com/watch?v=N06R1rFVQpA&t=666)]
We have to, we have to, we have to clean that up too.

##### **Geohot** [[00:11:09](https://www.youtube.com/watch?v=N06R1rFVQpA&t=669)]
What I would do for that is just put a, can you put an after, after the call and then put those buffers on the after?

##### **Nimlgen** [[00:11:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=678)]
Yeah. Yeah.

##### **Geohot** [[00:11:20](https://www.youtube.com/watch?v=N06R1rFVQpA&t=680)]
I think that's the way to do it. Right. Because that's what, what that's basically saying is like these buffers need to be kept alive during this call. So here's an after node that uses them.

##### **Geohot** [[00:11:35](https://www.youtube.com/watch?v=N06R1rFVQpA&t=695)]
Yeah. No, I need to get more strict about writing, about writing spec checks.

##### **Geohot** [[00:11:43](https://www.youtube.com/watch?v=N06R1rFVQpA&t=703)]
And making sure things like, yeah, like you can't have cast on the left-hand side of the store. You can't have a call that has a parameter mismatch. Yeah. Just, just after the buffers, I think is right for that.

##### **Nimlgen** [[00:11:58](https://www.youtube.com/watch?v=N06R1rFVQpA&t=718)]
Yeah. Cool. Yeah. I'll cover this the next week. Yeah. Actually, that's why I decided to rewrite it. I have the whole features and like the whole picture, like of the implementation. So yeah, I think a lot of things to clean up there.

##### **Chenyu** [[00:12:20](https://www.youtube.com/watch?v=N06R1rFVQpA&t=740)]
Right. Yeah. Moving on. Let's see our updates.

##### **Chrism** [[00:12:33](https://www.youtube.com/watch?v=N06R1rFVQpA&t=753)]
Yeah. So. You go to stats.tinygrad.win. You'll see the LLMs up there at the top, hopefully. So all of them, except for LLama3Beam4GPU are using tinygrad.LLM.

##### **Chrism** [[00:12:55](https://www.youtube.com/watch?v=N06R1rFVQpA&t=775)]
Just cause, you know, I still want it to have a multi GPU mark. Yeah. So that's good.

##### **Chrism** [[00:13:05](https://www.youtube.com/watch?v=N06R1rFVQpA&t=785)]
Woe has helped me put the actual correct units on the graph. So that's, that should be nice.

##### **Chrism** [[00:13:14](https://www.youtube.com/watch?v=N06R1rFVQpA&t=794)]
Yeah. What else?

##### **Chrism** [[00:13:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=798)]
I like tokens.

##### **Geohot** [[00:13:19](https://www.youtube.com/watch?v=N06R1rFVQpA&t=799)]
I like tokens per second.

##### **Chrism** [[00:13:21](https://www.youtube.com/watch?v=N06R1rFVQpA&t=801)]
Yeah. Yeah. It's nice. And then also the, he also made the other graphs actually have seconds as opposed to like no units at all.

##### **Chrism** [[00:13:30](https://www.youtube.com/watch?v=N06R1rFVQpA&t=810)]
Just helpful.

##### **Chenyu** [[00:13:32](https://www.youtube.com/watch?v=N06R1rFVQpA&t=812)]
So we try the tokens per second.

##### **Geohot** [[00:13:34](https://www.youtube.com/watch?v=N06R1rFVQpA&t=814)]
Before we didn't like it.

##### **Chrism** [[00:13:38](https://www.youtube.com/watch?v=N06R1rFVQpA&t=818)]
I know that.

##### **Chenyu** [[00:13:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=820)]
Oh, I don't know.

##### **Geohot** [[00:13:41](https://www.youtube.com/watch?v=N06R1rFVQpA&t=821)]
I think it's, I think it's.

##### **Chenyu** [[00:13:43](https://www.youtube.com/watch?v=N06R1rFVQpA&t=823)]
Yeah.

##### **Geohot** [[00:13:43](https://www.youtube.com/watch?v=N06R1rFVQpA&t=823)]
I think there's more.

##### **Chenyu** [[00:13:44](https://www.youtube.com/watch?v=N06R1rFVQpA&t=824)]
Last time the argument was you always want the numbers go to go down or something like that. Except for tokens per second, which you want to go up.

##### **Wozeparrot** [[00:13:52](https://www.youtube.com/watch?v=N06R1rFVQpA&t=832)]
I think LLMs now tokens per second is the metric that you go by. By, by, by.

##### **Chrism** [[00:13:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=839)]
Yeah. I mean, I've seen, the other thing I've seen is like the, like prompt processing and, um, What's the other one? Token generation?

##### **Chenyu** [[00:14:07](https://www.youtube.com/watch?v=N06R1rFVQpA&t=847)]
I'm just saying we had this before and we reverted. It's okay, it's okay.

##### **Chrism** [[00:14:13](https://www.youtube.com/watch?v=N06R1rFVQpA&t=853)]
Anyway.

##### **Chrism** [[00:14:15](https://www.youtube.com/watch?v=N06R1rFVQpA&t=855)]
If we need to change it, it's not a crazy thing to change. I did try out Docker. Unfortunately it was slower than the setup tinygrad stuff. This is in part due to the fact that the Docker image is kind of huge. And also just in part due to, like, you have to download it from GitHub servers. The Docker image has to be downloaded from GitHub servers. And it's just not the fastest thing in the world. And I think what you can do is you can split it up into a whole bunch of different layers. And then you can download all the layers in parallel. And then that should be faster because you sort of amortize this. For whatever reason, every individual connection seems to be slow. But then downloading all the stuff in parallel seems to be faster. But it didn't seem like a problem. It felt like I was just kind of shunting all the complexity inside setup tinygrad into a Docker file. And it wasn't actually really going to be all that simpler because we still need to do some stuff on macOS to setup tinygrad. And you can't run a Docker container on macOS. But anyway, when I was looking at that, I looked at a lot of the sizes of our dependencies in CI. And they really are that big. And they really are that big. And a lot of them are hard to slim down without compiling from source. So for instance, like, co-manager installs a ridiculous amount of dependencies despite the fact that we only need libAMD co-manager. And even libAMD co-manager is just like a big file. It's 150 megabytes.

##### **Chrism** [[00:15:48](https://www.youtube.com/watch?v=N06R1rFVQpA&t=948)]
And that's just because it statically compiles in basically everything. Wouldn't be that surprised if they compile with flags that are not optimal.

##### **Chrism** [[00:15:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=959)]
And then similarly, like, we also installed Mesa Vulkan shaders, which installs, like, all of X11. And also a whole bunch of, or sorry, Mesa Vulkan drivers. And Mesa Vulkan drivers installs a whole bunch of stuff that we, like, obviously we don't care about X11. But it also installs, like, the Asahi Linux driver. And this is just not, like, something that we, I don't understand why you would. And so, but this is a similar case for all of these dependencies where, like, we could definitely benefit in the size. But I compile from source ourselves and doing something similar to what Amai does with their dependencies repo. So that could be an option for trying to try to slim these down. It's worth the extra complexity there.

##### **Geohot** [[00:16:48](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1008)]
I think maybe the diminishing returns on this.

##### **Geohot** [[00:16:51](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1011)]
Yeah. Like, what's it going to take to get things down to, like, let's say two minutes?

##### **Chrism** [[00:16:58](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1018)]
Yeah. Yeah. I think we can get down to two minutes. Like, basically, most of the stuff that's above two minutes right now is all macOS. And so I think a lot of that, I think, okay, so a lot of the stuff that's slow on macOS is, like, Metal on macOS is actually decently fast. But, for instance, like, LLVM pipe on macOS or Clang on macOS or LLVM on macOS, those are all somewhat slow. And the thing is, like, those are probably adequately tested Linux on MacOS. And, you know, like, LLVM pipe Linux and LLVM Linux and Clang Linux. So it feels like a lot of that stuff could probably be, like, a we don't need to test so much stuff. Like, so Metal maybe should run the full suite. But I'm not necessarily sure that we should be running all of the tests for, you know, macOS Clang. Especially considering it's slow. Like, it just doesn't seem like Metal doesn't get tested at all otherwise. But, you know, like, LLVM is obviously already being tested. Yeah, I think that's just fine.

##### **Geohot** [[00:18:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1082)]
I mean, I would just, like, look at all the historical failures and see if it ever caught anything. If it didn't, then, yeah. Maybe just move to, like, a more Windows model for many of them. And then maybe you can even split Metal among two runners if that's easy.

##### **Chrism** [[00:18:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1098)]
Yeah, yeah. I'll double check with Metal. I'm pretty sure, yeah, Metal is actually decently fast, which is nice. The other ones that are slow... Sorry? Yeah.

##### **Geohot** [[00:18:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1109)]
I see 3 minutes 30 from Metal.

##### **Chrism** [[00:18:31](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1111)]
Okay. Yeah, the other thing is that it's pretty inconsistent. Like, sometimes it's fast and sometimes it's slow. So I'll have to look at more of them. Yeah. I've noticed, like, in the evenings it's faster and then in the mornings it's slower. So I might be able to figure that out. Yeah. The other thing is the OpenCL tests. So I looked at switching off of the Intel runtime. Unfortunately, Fockel is... It's just slow. Like, I tried it on my local computer. I tried it on Tiny R3 or R4. It's just slower than the Intel runtime. Yeah. And I also tried it in CI and it's also slower. And even with compiling, making sure that it's actually using the, like, optimized for, you know, Zen 4 or whatever that we're running on. It's still slow. I did try Rusticle. Which, Rusticle was actually somewhat promising. The performance is decent. Unfortunately, there are a couple of bugs in Rusticle. I got all of the backend test suite to pass except for two tests. And the broken stuff is... There's two bugs. One of them is related to some sort of constant folding issue that only happens when you, like, cast a short into a float. When you cast a... Yeah. When you bitcast a short into a float 16. There's some sort of bug in Mesa. So I have to open an issue for that. And then the other one... What was the other one? I don't remember off the top of my head exactly what the other bug was. But there was another bug. It was... Oh, yeah. It was... We have one test where we have, like, data dependent loading. So you use, like, one buffer to index another buffer. And this just hits, like, a weird code path in Mesa. And...

##### **Chrism** [[00:20:27](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1227)]
There's a bug in LVM pipe for that. So...

##### **Geohot** [[00:20:36](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1236)]
Yeah. Yeah. How does that compare to the Intel one?

##### **Chrism** [[00:20:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1240)]
Yeah. The performance is good. I haven't tested in CI. But on R4, it's actually faster than the Intel runtime. So I'll have to do a run in CI. But, yeah.

##### **Geohot** [[00:20:52](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1252)]
I like the idea of switching. I mean, it's not like the Intel one is perfect. We just have the workarounds baked in. Yeah. So we can't test all of our stuff in the code base.

##### **Chrism** [[00:20:58](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1258)]
Yeah, exactly. Oh, yeah. That was the other thing with that doesn't support create image 2D from buffer. So we can't really test all of our image stuff without that. Yeah. Yeah.

##### **Geohot** [[00:21:12](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1272)]
That's good. I mean, I definitely like the idea of moving something to moving to something open source. So... Yeah.

##### **Chrism** [[00:21:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1278)]
Yeah. So I think what I'll do is I'll open up issues in the Mesa bug tracker for those. I did open up. I opened one for the weird code path and LLVM pipe with the data dependent loading. And I did get a response on that. And someone's working on that. So that seems like they're actually pretty responsive about this. So if both of these things get fixed, that seems like a good sign that maybe this is usable. I was super worried that it was going to be like a ridiculous amount of bugs. It turns out that it seems like it might be pretty good.

##### **Chrism** [[00:21:54](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1314)]
So we'll see about that. Yeah. I think that's mostly it.

##### **Chrism** [[00:22:03](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1323)]
Oh, yeah. The other slow tests are the other CL tests. I guess these might be faster if we switch to Rusticle. We'll see. But for instance, like the generate data set, we run extra optimization generate data set. Is this... Like, does anyone use this? I haven't seen this fail before. Yeah. I've seen it fail, but only because of the Intel OpenCL runtime bug. Uploads a file like sops.gz. Does anyone use that?

##### **Geohot** [[00:22:37](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1357)]
Oh, I think some of the tests might use that. So sops.gz is just a bunch of cached kernels that you can then use whenever you need a data set of kernels. So I would see if anything uses that. And then also, you could probably move that to its own runner. Like, is that just one thing alone too slow?

##### **Chrism** [[00:23:01](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1381)]
Where is it running? It's running with some other stuff. I'll double check. It's part of CLMISC tests.

##### **Geohot** [[00:23:07](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1387)]
I don't know who made this.

##### **Chenyu** [[00:23:09](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1389)]
There used to be some tests that check all the optimization earlier. I don't know if it's deleted or commented. It's been surprisingly long. I feel we should update that. But we never update it, and nothing really breaks. So I don't really know what the current status for that.

##### **Chrism** [[00:23:30](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1410)]
Yeah. So we have this fused Optum test, and those are all skipped. And it might be external test aux that tests that.

##### **Geohot** [[00:23:45](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1425)]
Yeah, I don't know why all the fused Optum tests are skipped. That probably shouldn't be skipped. If nobody's using that data set, then we can probably just remove that and get rid of that whole runner.

##### **Chrism** [[00:23:57](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1437)]
Yeah, I'll double check that it isn't used by anything, but I'm pretty sure it isn't.

##### **Chrism** [[00:24:04](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1444)]
Cool.

##### **Chrism** [[00:24:04](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1444)]
I'm pretty sure I didn't see anything that was using that.

##### **Geohot** [[00:24:08](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1448)]
I mean, I'm just looking at the runners now. Yeah, getting rid of all these one-off random things would be nice. Yeah, CL tests should go. Yeah. I mean, like LLM. I mean, maybe some of these can just be improved in naming, too. But we have great names like Torch Backend Test and Torch Backend Test More.

##### **Chrism** [[00:24:30](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1470)]
Yeah, that one definitely could be cleaned up.

##### **Geohot** [[00:24:34](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1474)]
And then also, what about my thing about the LLMs? Why no Metal for Quen? Why no AMD for Alma?

##### **Chrism** [[00:24:42](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1482)]
Oh, well, so what I did was I was originally going to have them all run Quen and LLM. But I'll just say that I'm not sure. I think Quen was too big to fit on Metal.

##### **Chrism** [[00:24:57](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1497)]
I see.

##### **Geohot** [[00:24:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1499)]
I mean, yeah, I want the benchmark test to be refactored, kind of like you refactored the other tests, too. It shouldn't be duplicated. It should just run the same thing on both.

##### **Chrism** [[00:25:15](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1515)]
Oh, I see what you mean. Yeah, yeah. Like the matrix thing.

##### **Geohot** [[00:25:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1518)]
Yeah, yeah. It should be a matrix, right? Like, I don't like all of these one-off random things. Oh, I forgot to change that on that. And yeah.

##### **Chrism** [[00:25:27](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1527)]
Yeah, for sure. That makes sense. That's, yeah. Yeah, the reason I did that was because I just wanted to have like a MOE model and a dense one.

##### **Chenyu** [[00:25:39](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1539)]
Yeah, yeah, yeah.

##### **Chrism** [[00:25:39](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1539)]
The Quen that I chose.

##### **Qazalin** [[00:25:41](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1541)]
But...

##### **Geohot** [[00:25:43](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1543)]
I mean, if you can't run the Quen, don't run the Quen. But run Alma on all of them. Oh, yeah. Makes sense.

##### **Geohot** [[00:25:50](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1550)]
Yeah, okay. Alma, too. And then that's F16. Maybe we should also run a llama in Quant.

##### **Chrism** [[00:26:00](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1560)]
Yeah, sure. I had, yeah, previously I had that, but it was really slow to schedule. So I just didn't want to make the benchmark take away longer. But...

##### **Geohot** [[00:26:10](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1570)]
We should fix that one. It's so slow to schedule, right? These are good things. I mean, like, maybe that's an interesting thing. Yeah. Yeah. Maybe we should put that on the LLM benchmarks, too. What the total time is.

##### **Chrism** [[00:26:22](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1582)]
Yeah, yeah.

##### **Geohot** [[00:26:23](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1583)]
That makes sense. Or, you know, I mean, actually, the industry term is time to first token. Yes. Yeah. Like cold time to first token, right? There's like time to first token cold, and there's time to first token warm.

##### **Chrism** [[00:26:34](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1594)]
Yeah, yeah.

##### **Chrism** [[00:26:37](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1597)]
Yeah, that makes sense.

##### **Chrism** [[00:26:39](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1599)]
Jit Beam 2 is a reasonable value to be sitting there. Oh.

##### **Qazalin** [[00:26:45](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1605)]
Yeah.

##### **Geohot** [[00:26:46](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1606)]
Oh, no wonder it's super slow.

##### **Chrism** [[00:26:48](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1608)]
Oh, yeah. Yeah. Yeah. No, I mean, that's that's the reason it's not. It wouldn't be slow if I wasn't doing that.

##### **Geohot** [[00:26:52](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1612)]
But also if you're beaming it's loud. But yeah.

##### **Qazalin** [[00:26:56](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1616)]
Yeah.

##### **Geohot** [[00:26:57](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1617)]
Well, that's that's a really good number on that.

##### **Geohot** [[00:26:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1619)]
On that. One three five.

##### **Chenyu** [[00:27:00](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1620)]
Pretty good.

##### **Geohot** [[00:27:03](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1623)]
Yeah. Yeah. Okay. Yeah. But that's what the chip being.

##### **Chenyu** [[00:27:08](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1628)]
Yeah.

##### **Geohot** [[00:27:10](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1630)]
Cool. Yeah. There's definitely there's another week of test work.

##### **Wozeparrot** [[00:27:14](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1634)]
Yeah, I think. Yeah. Yeah.

##### **Chrism** [[00:27:20](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1640)]
There's another one that's also interesting. It's interesting that it's slower for the llama, but it's faster for the coin. I'm not sure what's up with that.

##### **Chenyu** [[00:27:28](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1648)]
We did put some time into that. Okay. Interesting. Okay.

##### **Chrism** [[00:27:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1660)]
I think that's that's all I have.

##### **Chenyu** [[00:27:44](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1664)]
Sounds good.

##### **Qazalin** [[00:27:45](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1665)]
Yeah. Yeah. Yeah. Yeah.

##### **Chenyu** [[00:27:47](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1667)]
Okay. Next llama training.

##### **Wozeparrot** [[00:27:50](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1670)]
Sorry. Fixing all of the MXFPA convergence issues and MXFPA now converges correctly. Good.

##### **Geohot** [[00:28:00](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1680)]
What was the issue?

##### **Wozeparrot** [[00:28:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1682)]
So there was a bug with a kernel that clausulin merged for the transpose BF16 gem under MP specifically. Okay.

##### **Chenyu** [[00:28:17](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1697)]
So I guess the bug is wrong or the output is wrong.

##### **Wozeparrot** [[00:28:21](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1701)]
There was a sum that across dimensions that didn't need to happen, depending on how you sharded.

##### **Chenyu** [[00:28:28](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1708)]
Okay. It's just not. How did you find that?

##### **Wozeparrot** [[00:28:36](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1716)]
You asked Claude to look at the bug. Great.

##### **Chenyu** [[00:28:39](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1719)]
Okay. So. Yeah. MP now. Yeah. Yeah.

##### **Geohot** [[00:28:49](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1729)]
Yeah. So. Yes. So MP, AB converges now MP, AP converges now.

##### **Qazalin** [[00:28:56](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1736)]
Okay.

##### **Chenyu** [[00:28:57](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1737)]
And do we have like, Oh, sorry. Go on.

##### **Qazalin** [[00:29:01](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1741)]
Okay. Yeah.

##### **Wozeparrot** [[00:29:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1742)]
And there was another bug where we were rerunning the in it way to randoms. Each step. This is contributing a lot to step time on the minibus. batches. So we're about five seconds faster than the batch forward-backward time with that fixed.

##### **Chenyu** [[00:29:28](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1768)]
Do we have a link to the latest? Latest is in progress right now. That's the one that's running.

##### **Wozeparrot** [[00:29:48](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1788)]
I started porting and what I'm going to work on next this week as well is continue porting the kernels that we use in DP to MXFP8 and MP.

##### **Geohot** [[00:30:01](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1801)]
I mean what I really want to do is get a 7db converged. Like you say it's too slow to run, like what do you mean by that?

##### **Wozeparrot** [[00:30:11](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1811)]
I mean we could run it but this ties up a machine for a week.

##### **Geohot** [[00:30:15](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1815)]
It's a week, okay.

##### **Geohot** [[00:30:16](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1816)]
Okay.

##### **Geohot** [[00:30:20](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1820)]
Yeah I mean so what's the path to making that a day? I see 2.2% MFU on that running link.

##### **Wozeparrot** [[00:30:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1829)]
Yes. I think that's about expected. It's really small shapes in BS1. We also... Oh I guess yeah it'll be better and it'll be better on 70 with the bigger... Yeah and we also don't use any of the custom kernels that we use for DP. So that's... What I'm doing this week is porting all those kernels over to MP and MXFP8.

##### **Geohot** [[00:30:52](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1852)]
Yeah it's annoying that I mean that's just like it's annoying. How different are the kernels for MP? How much can you kind of reuse and how much does multi give you versus having to like manually do that?

##### **Wozeparrot** [[00:31:05](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1865)]
I mean it's not just the MP that differs so like embedding will port over... Embedding like already works with MP. It's... You mean my customers? Yeah.

##### **Geohot** [[00:31:17](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1877)]
Like my customers embedding backwards.

##### **Wozeparrot** [[00:31:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1878)]
Yeah. It's mainly not the DP to MP porting. It's that we're porting from the FPA. A lot of the kernels are FUSE quantizes and they all quantize to FPA not MXFP8.

##### **Geohot** [[00:31:39](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1899)]
I see.

##### **Chenyu** [[00:31:42](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1902)]
So if you run the 70P now... What's the MFU? Do you have a number?

##### **Chenyu** [[00:31:51](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1911)]
I can pull last number. Oh sure. Do I have a number?

##### **Wozeparrot** [[00:32:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1922)]
I don't have a number right now.

##### **Chenyu** [[00:32:04](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1924)]
Okay. I think it's interesting to know what the number was and I guess what do we expect after we port all these kernels?

##### **Qazalin** [[00:32:14](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1934)]
Yeah.

##### **Chenyu** [[00:32:16](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1936)]
Because if it's like a week and I don't know how fast this can reasonably be but if it's say three days then I don't know. Like high innovation for four days doesn't sound that bad and it's nice to have... Yeah. Three days is a lot more reasonable than a week.

##### **Geohot** [[00:32:33](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1953)]
Yeah.

##### **Chenyu** [[00:32:38](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1958)]
How confident that if you just let 70 be run for one day and does that... In any ways help us to know if we are making something really bad?

##### **Wozeparrot** [[00:32:51](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1971)]
Fairly confident.

##### **Chenyu** [[00:32:54](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1974)]
Yeah. So I think it's a good idea to just let it run for one day and see what the curves look like. Because we also have like even bigger model after this. So I think it's more reassuring to know that at least 70B can run for some extended time. Then in parallel we also improve those.

##### **Wozeparrot** [[00:33:15](https://www.youtube.com/watch?v=N06R1rFVQpA&t=1995)]
Yeah. It is a bit nicer with the block scaled format that the numerical stability doesn't depend on the weight sizes. Yeah.

##### **Chenyu** [[00:33:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2009)]
I mean you know better. I just think it's good to always have some 70B run for maybe just a few hours is fine and making sure it at least looks good for a few hours.

##### **Wozeparrot** [[00:33:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2020)]
Yeah.

##### **Chenyu** [[00:33:42](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2022)]
And then it's also...

##### **Wozeparrot** [[00:33:46](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2026)]
I think a lot of our time right now is calm and it's unclear if we might need to do pipeline parallel. Supposedly that has better calm overlap than just tensor parallel.

##### **Geohot** [[00:34:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2042)]
I mean I think our calm might just be kind of bad. Maybe Guazalan knows about this? Yep.

##### **Chenyu** [[00:34:11](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2051)]
A little bit. I can talk about it more later. in my section, but basically we're just issuing too many small copies. Whereas we could just like bash them.

##### **Qazalin** [[00:34:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2069)]
Like AMD's equivalent number of like copy commands that it sends to GPU is like half ours.

##### **Geohot** [[00:34:37](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2077)]
Yeah. I mean, I think, yeah, it's copy slice, but there's also copy slice on the other side, right? There's also like reassembly unslice.

##### **Qazalin** [[00:34:46](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2086)]
Oh, the read the cat. Yeah. That one's also that runs on the GPU and blocks everything else. The other ones are just overlapped.

##### **Wozeparrot** [[00:34:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2099)]
This is probably just worse overall for TP then because it's just more on reduces happening.

##### **Chenyu** [[00:35:09](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2109)]
Okay.

##### **Chenyu** [[00:35:10](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2110)]
I think directionally we want to. Our. We want to prioritize the things that we know we would definitely need for four or five B. So if we are going to use these MX PA or FPA kernels, then we definitely need to do lows and we should do that fast. Then I think there are still some value to have a 70 B run for some time. So maybe a few hours is fine, but just so that I just want to look at the graph and see if it will converge.

##### **Chenyu** [[00:35:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2140)]
Okay. Sounds good. Anything else, George?

##### **Qazalin** [[00:35:45](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2145)]
Yeah. Yeah.

##### **Chenyu** [[00:35:48](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2148)]
Okay. Next.

##### **Qazalin** [[00:36:00](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2160)]
Last week's run versus the run that I just finished 15 minutes ago. It's the fastest we've had yet.

##### **Chenyu** [[00:36:11](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2171)]
Green.

##### **Qazalin** [[00:36:12](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2172)]
What's our task? We are at the end of the run. We are at around, I can share at around 1.54 to 1.61 seconds. And these at 1.3, 1.4. So we're like off by the 263 milliseconds with AMD.

##### **Geohot** [[00:36:38](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2198)]
Okay. So we're two hours and 47 minutes for the training.

##### **Chenyu** [[00:36:42](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2202)]
Yeah.

##### **Geohot** [[00:36:44](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2204)]
Do you see a good. Yeah. Do you see a good path to, to get it to, eat AMD?

##### **Qazalin** [[00:36:54](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2214)]
Beat AMD. I'm going to first match AMD this week. So yeah, I haven't merged anything yet. It's in a branch everything. I fixed copy, copy slice, and I've been going through the contiguous and fixing those. We're at about 5,900 kernels. So we're still off. So I'm going to first match AMD this week. Here we go. That was actually 44 hours from approvability. Yeah, I think if I can reach the inaccurate amount every, if I can tell what the Titans is, we can find it.

##### **Chenyu** [[00:37:32](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2252)]
Yeah.

##### **Qazalin** [[00:37:33](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2253)]
Yeah. That's my faktor. I don't want toちゃ Gid, The lot. Nope. That's probably what I'm aiming for. in this, you'll see that there's gaps.

##### **Geohot** [[00:37:51](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2271)]
There's gaps between the launches.

##### **Qazalin** [[00:37:54](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2274)]
Yeah. There's gaps between the launches. You see the graph tear down and stand up. So that's going to be all the speed that I've been getting so far is from just removing E-kernels.

##### **Geohot** [[00:38:10](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2290)]
I mean, I think removing E-kernels is great anyway. Like I think even the both kernel overhead and just wasted memory bandwidth.

##### **Qazalin** [[00:38:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2298)]
Yeah.

##### **Chenyu** [[00:38:21](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2301)]
Is the wrong 89 master like old master?

##### **Chenyu** [[00:38:26](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2306)]
Oh, no, no. This is my branch.

##### **Geohot** [[00:38:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2309)]
Oh, I mean, the slower winding graph.

##### **Chenyu** [[00:38:34](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2314)]
Yes, that was master.

##### **Geohot** [[00:38:48](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2328)]
Yeah. What I really want to know is like, yeah, what you think the timeline looks.

##### **Chenyu** [[00:38:54](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2334)]
I'm asking because after my invalid clone change, I think things got a bit faster because now. Yes, this is for master is for your team.

##### **Chenyu** [[00:39:06](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2346)]
Okay. This is before your last week. Yeah.

##### **Geohot** [[00:39:13](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2353)]
Sorry, George, go ahead.

##### **Geohot** [[00:39:16](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2356)]
Oh, yeah. And I just kind of want to like, you know, make sure we have some kind of idea of like timeline schedule for when for all the things we need to do to like, like, like a breakdown of all the tasks that are required to match and be

##### **Qazalin** [[00:39:37](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2377)]
well, I think the only task is removing E-kernels. That's basically what it's. Comes down to.

##### **Geohot** [[00:39:44](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2384)]
Well, I mean, removing E-kernels means a lot of things, right? Removing E-kernels like like even a breakdown of like, okay, what E-kernels do we have to remove? Why is our thing inserting them? How many of these things are generic? How many of these things are specific?

##### **Qazalin** [[00:39:57](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2397)]
Yeah.

##### **Geohot** [[00:39:58](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2398)]
But yeah, the end goal of this whole project

##### **Qazalin** [[00:40:04](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2404)]
is just.

##### **Chenyu** [[00:40:08](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2408)]
That's. Sure. A little bit about.

##### **Qazalin** [[00:40:12](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2412)]
My repulse so far. I've I've been basically working. On Lama layers, too. So that's what that was really fast. And the LLM can actually help me iterate on that. Lama layers to finish is very fast and is scheduled basically identical.

##### **Geohot** [[00:40:31](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2431)]
That's what is Lama layers to.

##### **Qazalin** [[00:40:34](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2434)]
Lama layers to just like decreases the scheduling time.

##### **Geohot** [[00:40:39](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2439)]
Oh, you mean the environment variable? Okay.

##### **Qazalin** [[00:40:42](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2442)]
Yeah. Yeah. The main one takes like two minutes. This one is like less than 30 seconds, 20 seconds. And so it's very fast.

##### **Chenyu** [[00:40:52](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2452)]
To iterate on.

##### **Qazalin** [[00:40:56](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2456)]
And yeah, I think I think until end of this week, I'm going to just work on a branch similar to how you did the DSP contract and then like figure out how to polish and merge things one at a time carefully. And.

##### **Geohot** [[00:41:12](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2472)]
Yeah.

##### **Qazalin** [[00:41:13](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2473)]
Yeah. Like my copy slice. I'm not very happy with how I did it, but it works. So there's many things in that branch.

##### **Chenyu** [[00:41:24](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2484)]
Should be polished and then merged correctly.

##### **Geohot** [[00:41:31](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2491)]
Yeah. I really want to do two things next MLperf. I want to comfortably be there 8B and get 4 or 5B.

##### **Qazalin** [[00:41:41](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2501)]
Yeah. I think that's a good question. Yeah. I'll see if we need a better gem because our gems and flash extensions are also slow.

##### **Geohot** [[00:41:50](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2510)]
Yeah.

##### **Geohot** [[00:41:51](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2511)]
I think that's the last thing I'm worried about. I mean, once we have it like just like, oh, this is a gem. Okay, great. Like that's a totally like orthogonal problem to, you know, there's too many kernels.

##### **Geohot** [[00:42:06](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2526)]
Like the gem thing is kind of. The gem thing is kind of unrelated to tiny grad in a way that like. You know, in a way that we're looking at it now.

##### **Qazalin** [[00:42:15](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2535)]
Yeah.

##### **Geohot** [[00:42:19](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2539)]
You know, if the improvement from embellic long stack with your stuff.

##### **Qazalin** [[00:42:24](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2544)]
Yes. In those quantities help.

##### **Chenyu** [[00:42:28](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2548)]
That's nice. Happy surprise. Yeah.

##### **Geohot** [[00:42:35](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2555)]
Anything else?

##### **Qazalin** [[00:42:38](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2558)]
That is all. Yeah. Bye. Bye. Anything else I would mention is that I still don't copy was mentioned. I'm not sure if the way we do our copies with many like small launches, every copy op gets mapped to a GPU command is correct. It's like there seems to be that they patch things into.

##### **Geohot** [[00:43:09](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2589)]
Yeah. I mean, we also don't have to use the. The SDMA engine. This is more of an emulsion thing. Right. So there's two ways to do copies. You can either do copies with kernels or copies with the SDMA engine. And I imagine for really small copies, there's overhead. I mean, yeah, we could also just combine all the copies into one kernel.

##### **Chenyu** [[00:43:30](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2610)]
Yeah.

##### **Geohot** [[00:43:32](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2612)]
I mean, but that gets more to. I mean, this is kind of the project after HQ two. It's kind of going to be like. Okay, then like, why do we even have kernel boundaries here? But. This still doesn't like there's two things to separate here, right? There is the. We have launch kernel overhead, which we can improve from a runtime perspective versus the schedulers inserting extra e kernels, which is very worth fixing now because that's not going to be fixed by an omega kernel or something.

##### **Chenyu** [[00:44:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2642)]
Yeah. I'll continue looking on. The rest of the e kernels.

##### **Qazalin** [[00:44:13](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2653)]
Okay.

##### **Chenyu** [[00:44:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2658)]
Moving on. Next is my stuff.

##### **Chenyu** [[00:44:21](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2661)]
So I finally, after reverting like three times, I fixed the invalid cold thing. So the end effect is the const always have source empty null. There's no like unique const and stuff like that. So I closed the issue. I think I've done everything I wanted for the const. So next is I'm going to change this tensor dot training and tensor dot train thing to just be a context var. I'll probably just merge the intermediate stage that supports both. Then I will fix the const. So once that is tested and for everything else, if it's not tested, you should update it. Then once we are happy, I will delete the old tensor dot training thing.

##### **Geohot** [[00:45:19](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2719)]
Yeah. I mean, I think regardless of what we do with that, the source of truth should definitely be a context var. I don't know if we still want the helper method on tensor just to keep the API consistent.

##### **Chenyu** [[00:45:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2729)]
Yeah. So if you see my change, I just have a thing that reads from the context var to support the old API. And I will update everything we test and the things I know in MLPerf, but everything else. The goal is to eventually delete that training, I think. Or at least the dot train thing. Tenser dot train was another context var-ish thing that we probably don't want to support.

##### **Geohot** [[00:46:05](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2765)]
Wait, which one? Yeah.

##### **Chenyu** [[00:46:07](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2767)]
We also have tensor dot train.

##### **Geohot** [[00:46:10](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2770)]
That's different from training?

##### **Chenyu** [[00:46:12](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2772)]
That's different from training, yes.

##### **Geohot** [[00:46:13](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2773)]
Oh, God. All right. Yeah, delete this. Yeah, yeah. No, invalid clone try three is a very nice PR. Just the deletion of that transform unique const thing, that was terrible.

##### **Chenyu** [[00:46:29](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2789)]
Yeah. And I think if we want, I can also look into just empty. You can use the invalid. I think it's valid const now, I believe. So it doesn't need to be like a buffer. It can be constant valid if we want to do that now. Oh.

##### **Geohot** [[00:46:47](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2807)]
Wait. No, it can't be. What? If constant valid, is that unique?

##### **Chenyu** [[00:46:57](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2817)]
Const invalid clone.

##### **Geohot** [[00:47:01](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2821)]
Const invalid clone. Yeah.

##### **Chenyu** [[00:47:04](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2824)]
Yeah. So anonymous buffer is constant valid clone.

##### **Geohot** [[00:47:11](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2831)]
Yeah, but that's basically, like empty is just a subset of that. I wouldn't replace empty with constant valid clone.

##### **Chenyu** [[00:47:25](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2845)]
OK.

##### **Geohot** [[00:47:28](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2848)]
Right? Because clone is basically the creation of a buffer and a store.

##### **Chenyu** [[00:47:32](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2852)]
Uh-huh.

##### **Geohot** [[00:47:33](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2853)]
Like sure, that store is a no-op. Yeah. But like that no-op, like there's no reason to insert that in the graph.

##### **Chenyu** [[00:47:45](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2865)]
You know what I mean?

##### **Geohot** [[00:47:46](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2866)]
Like if you do like tensor.empty, right, there's no reason to like, it just, when you think about what a const invalid store is, a constant valid store is just a no-op. So that's basically just saying like, if I say constant valid clone, I'm saying create a constant valid. Clone says create a new buffer and then store this no-op. So I'm just saying like, if I say, like, I'm going to do this thing to a buffer, which is basically just a no-op.

##### **Chenyu** [[00:48:08](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2888)]
Uh-huh.

##### **Geohot** [[00:48:09](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2889)]
Yeah. So I just, I wouldn't replace like tensor.empty with it at all.

##### **Chenyu** [[00:48:14](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2894)]
OK.

##### **Geohot** [[00:48:16](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2896)]
The other thing that's like kind of related to this, I think also we could get rid of, I think we can get rid of unique entirely and just move to the new style buffer.

##### **Geohot** [[00:48:26](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2906)]
Oh, sure.

##### **Chenyu** [[00:48:28](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2908)]
I don't know if that interests you. I mean, if it's easy, sure. I don't know where we can get that. Do we still use it?

##### **Geohot** [[00:48:37](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2917)]
Well, all the buffers in the tensor graph are still like, you can see the one in that screenshot I posted. Yeah, they still have unique and device as sources. So now buffer has an arg, a param arg, and you can like put the...

##### **Chenyu** [[00:48:54](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2934)]
Those things live in param arg.

##### **Geohot** [[00:48:57](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2937)]
Yeah, those things live in param arg, right? There's no reason that we should have a device uop. It doesn't make any sense.

##### **Chenyu** [[00:49:03](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2943)]
So how does it do? Or like, how does it to be unique with that?

##### **Geohot** [[00:49:08](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2948)]
Oh, there's the first arg, the first field in param arg is called slot. That's basically what unique needs to be.

##### **Chenyu** [[00:49:17](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2957)]
OK. And that's currently like the distinguish buffers or param. Yeah, yeah, yeah.

##### **Geohot** [[00:49:24](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2964)]
It's just called slot. It's also like, so buffer is now used for define local and define reg. And it's just like slot is like how you do.

##### **Chenyu** [[00:49:32](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2972)]
OK. Sure. I can check. Another thing I'm interested is the disallow broadcast. I think it helps me somewhere for the wear and cast. I'm semi interested in that.

##### **Geohot** [[00:49:51](https://www.youtube.com/watch?v=N06R1rFVQpA&t=2991)]
So the main reason I added that flag, I mean, the broadcasting is correct. But the main reason I added that flag is you don't want to accidentally end up with broadcasting.

##### **Chenyu** [[00:50:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3002)]
Yeah, but we...

##### **Geohot** [[00:50:08](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3008)]
I mean, I need it for new code gen anyway.

##### **Chenyu** [[00:50:11](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3011)]
Yeah. So if it's needed anyway, then... I don't know. I don't think about it. I'll play it with this flag and see if it really helps me.

##### **Geohot** [[00:50:30](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3030)]
Yeah, yeah. Just like, yeah, we don't want to accidentally end up with it because, like, I often write bad things, and then I don't want to go back to it. But I'm like, OK, so this is the bug, the bug. Yeah, this is very hard to debug.

##### **Chenyu** [[00:50:37](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3037)]
You can only tell from the end shape or something like that.

##### **Geohot** [[00:50:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3040)]
Yeah. I mean, yeah, broadcasting is just a potential source of tons of bugs, like, yeah. Yeah.

##### **Chenyu** [[00:50:47](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3047)]
Anyway, Tensor now is like 500 lines. Great. And I think toward the end of this, I will also think about how to migrate to a new style, so that Tensor no longer inherits from mixing. But we can probably just say, yeah, I'm good. I'm going to go back to this because next week.

##### **Geohot** [[00:51:07](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3067)]
Yeah, yeah. We got to do I see BitCast is still here, too. We got that. We got to do BitCast.

##### **Chenyu** [[00:51:11](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3071)]
I have a floor because the back we still have back.

##### **Geohot** [[00:51:16](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3076)]
I mean, I'm working on it.

##### **Chenyu** [[00:51:19](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3079)]
I'm saying, yes, that's the only reason because it's there. Got it. OK, yeah, that's my pretty much my part. And we can move on to your part.

##### **Qazalin** [[00:51:30](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3090)]
Cool.

##### **Geohot** [[00:51:33](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3093)]
Yeah. So, you know, there's a lot to do before. Before VAC removal, I did so back back is now gone from all of the renders. The X86 renderer was the last one that still used it. Actually, the X86 renderer still used it internally, but the boundary doesn't have any VACs. So last week, I mostly worked on getting rid of Define Local, Define Reg and Define Var. So the new system, very simple. There's two things. There's buffer and buffer. And there's param. Right. So buffer and param are similar. But the thing is, param means bind it to something in an external scope, whereas buffer means create this variable in a local scope. Whether it's a local or a reg is just determined by the address space arg on param. So you can you can say it's local. You can say it's a reg. These things are not really that different. It's interesting when you really start to look at like what the address spaces are and the different back ends. So like in C, there's no difference between a local and a reg. They're exactly the same thing. But then on the GPUs, you can have this special modifier which puts something in this local memory. And then like also in C, when you do something like int a sub 16, what does that actually do? Is that in registers? Is that on the stack? Is that on the heap? What does the stack and heap even mean on a GPU? And the answer is it's usually in registers, but sometimes it's spilled to something called 2D. It's a little bit of a scratch, which is yeah. So basically, buffer and param are the new defined for anything. And this also like there's no reason like we used to have this really weird distinction about like, okay, so we had this buffer, which is like a long scoped buffer. And then we had a buffer, which is just like a temporary buffer. And the answer to that difference is that the long scope buffers are params and the ones that just exist in the scope of the function are buffers. So, yeah. That is the main thing I worked on last week. I also have tried a few times. I linked my PR to switch to the new code gen. The new code gen is mostly just a rewrite of the expander and the de vectorizer. So the expander used to propagate this thing through the graph that would do expansion. You know, that would convert. Basically. Base D types into D type Vex. Now that's all represented in the shape. So all you need to do is replace the upcasted ranges with like a stack of consts that shaped correctly. And then broadcasting handles the rest. So the expander became very, very short. And the de vectorizer is similar to the old de vectorizer. There's just a lot less like kind of cruft in there now. So it's just kind of cleaner. But yeah, the de vectorizer basically you can't actually on a GPU do like, you know, two things that are size 16 added together. You have to split it into 16 different ads. So that's what the de vectorizer does.

##### **Geohot** [[00:54:47](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3287)]
Yeah.

##### **Geohot** [[00:54:50](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3290)]
So hopefully that gets merged this week. And then there's no more D type Vex being created anywhere in the code gen path.

##### **Qazalin** [[00:54:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3299)]
I think.

##### **Geohot** [[00:55:01](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3301)]
Yeah. There's been a lot of like tightening of the spec.

##### **Geohot** [[00:55:05](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3305)]
Like now I can look at those like index cast thing and be like, no, no, no, no. It should be this right. Like we now have we now have a good language to say this is what it should be. And I think that the key insight is, well, OK, the ultimate end of this project is the removal of D type from UOP. UOP should not have D type. D type should be a derived property, a recursively derived property.

##### **Chrism** [[00:55:31](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3331)]
Yeah.

##### **Chenyu** [[00:55:32](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3332)]
And then that's kind of the end of the D type project.

##### **Geohot** [[00:55:40](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3340)]
And we're pretty much just more after the removal of Vex.

##### **Chenyu** [[00:55:49](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3349)]
Because the only thing that can generate D type is either a buff or the cost or a cast.

##### **Geohot** [[00:55:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3359)]
Yeah. Buff, const, param, cast, bitcast. They're the only things that can change D type.

##### **Chenyu** [[00:56:03](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3363)]
Cool. OK. So we go with comma. And any comment on the GLM effort in the general channel?

##### **Chrism** [[00:56:18](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3378)]
I think comma is happy. I bumped them last week. They needed like a real change to their code to support the new 8 range without device. Yeah. But I think that should be good to auto bump from now on. I'll double check that that goes successfully today. Yeah. No, I think there was some talk about they want to run both models simultaneously now. So they're going to run one model on the eGPU and one model on the device so they can automatically fall back if something happens to the eGPU. So there's some complaint about 90 grads. Like umm- This is by Farid. Doesiping theoh, think they're going to actually refresh their embeds? Uh, not yet. If the output of this model is not ready by X time, then give me the output of the other model. So instead, they're just going to run two model runners. And it would be nice if there was less overhead, because then they could put them both on the same core that they're already using for the model runner.

##### **Geohot** [[00:57:42](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3462)]
TinyGrad absolutely shouldn't have functionality like that. They should run two model runners.

##### **Chrism** [[00:57:47](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3467)]
Yeah, yeah. But in that case, it would be nice if we had less CPU overhead.

##### **Chrism** [[00:57:53](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3473)]
I mean, HTTQ2 hopefully should do this. Yes, that, yeah.

##### **Geohot** [[00:57:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3479)]
The right solution here is just ACQGL.

##### **Chrism** [[00:58:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3482)]
Yeah. And then there's always just some murmuring about, oh, it would be nice to have DSP support, or it would be nice to not rely on the Qualcomm CL stuff anymore.

##### **Chrism** [[00:58:16](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3496)]
And yeah, so we'll see.

##### **Geohot** [[00:58:20](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3500)]
I mean, I'm all for switching to Mesa. DSP support is, I'll be back in the office in July. We can plan out. I'll be back. July 2nd, we can plan out DSP support.

##### **Chrism** [[00:58:32](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3512)]
Yeah, yeah, yeah. Yeah, DSP, like, yeah. And then, yeah, even an assembly backend for Adreno.

##### **Geohot** [[00:58:41](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3521)]
I don't know about that. But we can switch them to Mesa if it's faster. That's fine.

##### **Chrism** [[00:58:46](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3526)]
Yeah, I don't think it's faster. It may be nicer for them to distribute.

##### **Chenyu** [[00:58:52](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3532)]
I'll talk to them about it.

##### **Qazalin** [[00:59:00](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3540)]
Cool.

##### **Chenyu** [[00:59:02](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3542)]
Thank you. Man, that's reasonable.

##### **Geohot** [[00:59:08](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3548)]
Yes, yes. I mean, use it for a good reason. And you actually Nan and me can do the gecement lifestyle now. Doesn't come with any adapter, but. V лайks folder, I'm using. Is not innovation an affirmation to me, I really like it. So it does need support, but keep it close to work. And that's good enough. GLM runner, it's like double the speed of any of the coding plans. Most of the coding plans give you like 50, 60 tokens per second. This is 100. I want it to go even faster. At 500 tokens per second, this is unquestionably the best LLM experience in the world.

##### **Geohot** [[00:59:45](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3585)]
So yeah, I won't try it. I'm happy with it.

##### **Qazalin** [[00:59:49](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3589)]
Great.

##### **Chenyu** [[00:59:52](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3592)]
Cool. I think that's about it for this meeting. Anything else?

##### **Geohot** [[00:59:59](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3599)]
We potentially have a very exciting deal with AMD.

##### **Geohot** [[01:00:04](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3604)]
Yeah, yeah, yeah, yeah. But hopefully, hopefully, we'll see.

##### **Chenyu** [[01:00:07](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3607)]
Great.

##### **Geohot** [[01:00:08](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3608)]
Sounds good.

##### **Chenyu** [[01:00:09](https://www.youtube.com/watch?v=N06R1rFVQpA&t=3609)]
OK, thank you, everyone. See you next week. Bye bye. Bye.
