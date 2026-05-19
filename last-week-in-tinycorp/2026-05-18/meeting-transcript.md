# 2026-05-18 Meeting

### Meeting Agenda

**Time:** new meeting #19, 5/18 9am Monday San Diego time
- company update
- const, requires_grad
- uop specs
- arch, dtype
- hcq2
- viz
- mlperf llama
- bounties, issues, comma happiness


### Audio

[Youtube Link](https://www.youtube.com/watch?v=s0VinPJFDeI)

### Highlights

- **[Company Update](#geohot-000002)**: Marketing helped restart sales; TinyBox Pros are back in stock with three orders, one already paid.
- **[Chestnut Launch](#geohot-000042)**: Chestnuts are delayed, and the launch should include modern LLM benchmarks to counter the perception that the tinygrad driver is slow.
- **[AMD MI300 Opportunity](#geohot-000220)**: AMD visited, and tinygrad is exploring whether broken MI300s with partial HBM failures could become a useful product.
- **[Gradients and Const Cleanup](#chenyu-000346)**: `requires_grad` is being phased out in favor of explicit `detach` for stopping gradients and a possible `is_param` field for optimizer/state handling.
- **[Const Without Device](#chenyu-000712)**: The plan is to delete `unique const` and make const/arange-like values deviceless until a real buffer boundary is needed.
- **[Minigen and UOp Specs](#geohot-000927)**: Minigen is being built as a minimal codegen path where every rewrite rule maps to a concrete action like adding accumulators, moving values to registers, or concretizing types.
- **[Binary and Replicated UOps](#geohot-001438)**: The UOp spec now lives in the tinygrad repo, adds `binary` as a deviceless graph-resident buffer-like constant, and introduces `replicated` as the cleaner direction for multi/sharding concepts.
- **[Arch and DType Support](#chrism-001815)**: Architecture cleanup now queries real device extensions, so FP16 and other dtype support can be determined per backend instead of relying on platform assumptions.
- **[MLPerf LLaMA Sprint Goals](#geohot-002535)**: The AMD contract team’s next goals are full correct 405B training, faster 8B training, and 8B training across both machines.
- **[HCQ2 Direction](#nimlgen-002634)**: HCQ2 has an implementation in master supporting graph/runtime paths, with multi-GPU still pending and old patch/non-custom firmware paths being removed.
- **[ROCm Regression](#qazalin-003328)**: LLaMA regressed after a ROCm upgrade; beam compilation hangs and GEMM performance dropped sharply, so the team decided to revert to ROCm 7.1.
- **[Custom Kernels to UOps](#geohot-003552)**: LLaMA speedups should move custom HIP/C kernels into low-level UOps so they remain within the UOp spec and can be reasoned about and optimized.
- **[Release and 405B Work](#chenyu-004429)**: The team plans to cut a release this week, ensure AMD-related work ships, and continue tracking 405B memory regressions.
- **[Comma CAFormer Target](#geohot-005705)**: Comma provided a CAFormer M36 model running around 100 ms, with a target of 33 ms requiring roughly 350+ GFLOPS and possibly hand-tuned GEMM work.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=s0VinPJFDeI&t=0)]
So, company update.

##### **Geohot** [[00:00:02](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2)]
I was in marketing last week. All my products are back in stock. We have three orders.

##### **Geohot** [[00:00:08](https://www.youtube.com/watch?v=s0VinPJFDeI&t=8)]
Marketing works. We have the project we don't talk about. Chenyu's here in the office. Chestnuts are delayed. I don't know.

##### **Geohot** [[00:00:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=27)]
It's like... My team is like... I had some deadlines for when we shipped them. We could meet that deadline, but it's going to cost 30% more to make them.

##### **Geohot** [[00:00:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=36)]
I'm like, eh, I don't think that's worth it. Maybe it's worth it?

##### **Geohot** [[00:00:42](https://www.youtube.com/watch?v=s0VinPJFDeI&t=42)]
But... Yeah, I think like... Someone did some Mac eGPU stuff, and now the tinygrad driver has a reputation for being slow. Because Alex Ziskind put that YouTube video out and didn't know about `BEAM=2`. So... Um... Yeah, I think that when we launch the Chestnut, we have to like... include a whole bunch of benchmarks for LLMs. Because it's really not slow. Our LLM speeds are quite similar to...

##### **Chenyu** [[00:01:14](https://www.youtube.com/watch?v=s0VinPJFDeI&t=74)]
News cycle management?

##### **Geohot** [[00:01:17](https://www.youtube.com/watch?v=s0VinPJFDeI&t=77)]
News cycle management? No, it's not news cycle management. I mean, the news cycle... I'm not trying to like... Like, like... manage news cycle. I'm just trying to make it like...

##### **Chenyu** [[00:01:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=87)]
I think if we want to sell this... Probably should make eGPU good. Exactly. Make like... a use case that we personally would want to use.

##### **Geohot** [[00:01:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=101)]
Well, yeah. And I think we have to also switch out... I think it's part of the test project. We gotta switch out all those old LLaMA benchmarks that nobody uses for like... modern... modern LLM benchmarks across different hardware. Yeah. Yeah. Yeah. Yeah. Those are our products in development. But TinyBox Pros are selling again. So that's good. Yeah. So we got three orders. One paid. My guess is one more will pay and one won't.

##### **Geohot** [[00:02:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=132)]
Great.

##### **Qazalin** [[00:02:13](https://www.youtube.com/watch?v=s0VinPJFDeI&t=133)]
Yeah.

##### **Chenyu** [[00:02:15](https://www.youtube.com/watch?v=s0VinPJFDeI&t=135)]
More expensive? More expensive? More expensive? I heard a price is going up.

##### **Geohot** [[00:02:20](https://www.youtube.com/watch?v=s0VinPJFDeI&t=140)]
Oh yeah. Our supplier, NVIDIA PM, said that the price is going up. For both 5090s and the other thing. And Blackwell. Yeah. Yeah, prices are going up. Oh, and we had AMD visit last week. That was pretty cool. So I emailed AMD leadership about... buying lots of broken MI300s and like... kind of like... kind of making them kind of work, and then selling them. There's lots of... there's lots of MI300s that have broken HBM RAM. So... The MI300 has... 192 gigs of RAM. Apparently that's 96 RAM dies. And it's... HBM is just stacks. So it's like 8 stacks of 12 or whatever. So... But if one of those dies breaks, the whole GPU breaks. Because there's no way for them to use it. But it still has 190 gigs of RAM. So... If we can buy broken GPUs... Then... Yeah, we're in luck.

##### **Geohot** [[00:03:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=206)]
I think that would be a cool... product to sell. See if that panned out.

##### **Qazalin** [[00:03:34](https://www.youtube.com/watch?v=s0VinPJFDeI&t=214)]
Okay.

##### **Chenyu** [[00:03:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=216)]
Sounds good. Moving on... That is my item. So I opened two issues.

##### **Chenyu** [[00:03:46](https://www.youtube.com/watch?v=s0VinPJFDeI&t=226)]
For... I don't know. The idea is... Now everything... left in Tensor is some kind of project. And two big ones are... The important one is... `requires_grad`. It was a Torch concept... to basically use that... to track gradients. But for our gradients... it really depends on... what do you do with the gradients. Since tinygrad is lazy, if you don't use it, then it's fine to have it. So now... The plan is to... I already pretty much removed all the usages... of `requires_grad` when working with gradient. And those are all fine. In the future if you want to... stop gradient from flowing... you just use detach. Detach will stop your gradient. And... Now it's slightly blocked by const, which I will talk later. But the idea is... to replace `requires_grad` with another field. Probably called `is_param` or something like that. So in the optimizer we know what... what are the weights there. That is the parameter. When you call `get_parameters` or `get_state`, it returns the things you expected to return. And speaking of const... Const is annoying. The fact that const has device... has a lot of... created a lot of issues. For... for symbolic shape... to symbolic tensor... to... any stuff. Yeah, so the idea is... Const will stay in... pure const without a device. Then there are boundaries... when you... need to have a... make a device. So for example... now when we call tensor... or as `Tensor.zeros`, there is a concept called... unique const. That is kind of a hack to tell you that... this const needs to be treated as a buffer. When you accumulate... gradients... it shouldn't... fly with another const zero. The new design... I put in the issue... that I'm still working on. Is... basically we find all the boundaries that... you want this to be a buffer. And then we... make a clone to make it a buffer. For example... if you do `Tensor.ones`, I think we just make it a buffer. And if you really want the... version that will fuse... you just go... `Tensor.const` or...

##### **Geohot** [[00:06:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=396)]
By make a buffer... You mean a named buffer.

##### **Chenyu** [[00:06:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=401)]
Yeah.

##### **Chenyu** [[00:06:42](https://www.youtube.com/watch?v=s0VinPJFDeI&t=402)]
Like store to...

##### **Geohot** [[00:06:44](https://www.youtube.com/watch?v=s0VinPJFDeI&t=404)]
Yeah I mean it's kind of crazy that... .empty makes a buffer... And .full makes this unique const thing. We can just make it a buffer.

##### **Chenyu** [[00:06:53](https://www.youtube.com/watch?v=s0VinPJFDeI&t=413)]
Yeah.

##### **Geohot** [[00:06:54](https://www.youtube.com/watch?v=s0VinPJFDeI&t=414)]
And like there are some little edge cases... Where if you do like... `Tensor.ones` plus one... It won't exactly fuse but don't do that.

##### **Chenyu** [[00:07:01](https://www.youtube.com/watch?v=s0VinPJFDeI&t=421)]
There are a bunch of... Edge cases that I'm still fleshing out. There are...

##### **Geohot** [[00:07:09](https://www.youtube.com/watch?v=s0VinPJFDeI&t=429)]
This doesn't delete unique const entirely.

##### **Chenyu** [[00:07:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=432)]
Yes so we will delete unique const. We will delete Tensor front UOp. Which is absolutely... That was... That there are still some cases like... What do you do with like... pad or... arange. I think by the same logic it shouldn't have a device. Then you start to worry about... What do you do if you have a const... Or if you have an arange... Then you do `.to`, `.shard`... Like do you really do those? But I think these are something that... We can just define and have the same behavior... And it should be good.

##### **Geohot** [[00:07:46](https://www.youtube.com/watch?v=s0VinPJFDeI&t=466)]
Well I mean hopefully this will fix some of like... The shard and const.

##### **Chenyu** [[00:07:51](https://www.youtube.com/watch?v=s0VinPJFDeI&t=471)]
I think it's another issue because that goes into like... Multi... Multi... Multi...

##### **Geohot** [[00:07:59](https://www.youtube.com/watch?v=s0VinPJFDeI&t=479)]
Yeah... No I'm saying like... When you... Right now if you create an arange... It's created on a device and then you shard it... It will actually like materialize that and then shard it. We absolutely don't want to do that.

##### **Chenyu** [[00:08:11](https://www.youtube.com/watch?v=s0VinPJFDeI&t=491)]
But it's like... Or maybe a reverse. Multi is weird.

##### **Geohot** [[00:08:18](https://www.youtube.com/watch?v=s0VinPJFDeI&t=498)]
It's just the idea of like it just doesn't have a device... is a lot cleaner. The idea of const not having a device is a lot cleaner. Because now when you do a const copy... it's no object.

##### **Chenyu** [[00:08:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=507)]
Yeah so I think this is for const device. And another... semi-related project is... an arange concept of dtype. So we have a concept for weak int. Maybe we want a weak float. Everything coming from like... Python as a weak type that we lower to a concrete type at some point. But... that's probably after the device. I think these... device, dtype... and the shape... is kind of getting weaker... and weaker in general. But I think we are finding good rules to... unify these.

##### **Geohot** [[00:09:04](https://www.youtube.com/watch?v=s0VinPJFDeI&t=544)]
What do you mean by weaker?

##### **Chenyu** [[00:09:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=545)]
Weaker as in everything is broadcasted... And like the actual thing is deferred... Decided later.

##### **Geohot** [[00:09:11](https://www.youtube.com/watch?v=s0VinPJFDeI&t=551)]
Yeah yeah yeah. Well yeah deferred Dtype is a big change I think.

##### **Qazalin** [[00:09:16](https://www.youtube.com/watch?v=s0VinPJFDeI&t=556)]
Yep.

##### **Chenyu** [[00:09:18](https://www.youtube.com/watch?v=s0VinPJFDeI&t=558)]
That's about it. And we can move on...

##### **Geohot** [[00:09:22](https://www.youtube.com/watch?v=s0VinPJFDeI&t=562)]
To spec.

##### **Qazalin** [[00:09:24](https://www.youtube.com/watch?v=s0VinPJFDeI&t=564)]
Cool.

##### **Geohot** [[00:09:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=567)]
So... This is minigen. Um... It works...

##### **Geohot** [[00:09:34](https://www.youtube.com/watch?v=s0VinPJFDeI&t=574)]
For most... Things now. It's just an absolute minimal codegen. And it says like... Okay these are the actual things you need to do. Like reduce isn't allowed in program. Okay so we have to actually assign like a... real place for the reduce to happen. That's like a real thing. Like none of these... Every single rule in the minimal codegen... and the codegen in general... should be tied to something that's like... understandable. It should be tied to like a real like action. Like not like... Oh well we transform from this form into this form. That's meaningless. Right? Like what are you actually doing when you transform from this form to this form. Um so like the top one... If you see that thing I linked... It's like reduce is not allowed in programs. And the reason reduce is not allowed in programs... is because you need an accumulator to actually do that reducing. So this adds that accumulator. Okay so then the next one is called... add loads. Um so that's not... That's poorly named. That should really be... move things into registers. Right so what load is... Load... That's one of the things we clarified a lot in the spec last week. Load is... Load is a real thing. Load is basically an anonymous store. Um and the way that we use it right now... is that load moves from the address space global... into the address space reg. Because when you have something like add... add can't... operate on globals. Right if you have like an add instruction on a GPU... the parameters are not globals. Now in x86 they might actually be globals. But in GPUs they're not. They need registers. So it moves it from one address space to another address space. Um and I think that's... I think we... load and copy and contiguous are all the same thing. Um load is just... store to an anonymous buffer. Then like here. We need to lower weak int for the program. Okay that's a pretty real thing. I mean my thing that actually does it is... is too simplistic. But the idea of like we need to concretize types. That's like a real... Okay. Move gates from index to load and store. So I think that can be a little bit more fleshed out. But what that actually means is those indexes have invalids. And invalid is not renderable. We actually need to move those invalids to something that is... that is... that is a verb. Right like it's a gated store. Like a... Well you passed the invalid right. That's a sentinel. Um and then like split ends. Renderable ends can only end one range. That one is a little bit... it's just like when an end has like three ranges. It turns it into three ends. I don't know. I don't know how I feel about that. So you can decompose ops like sine and threefry to renderable versions. And then add control flow edges where they're needed. And that can be a little more fleshed out too. But like there's your minimal codegen. And I'm going to keep working on that this week. Before we try to go to things like `dtype.vec`. Every time I try `dtype.vec`, you just end up in... you're rewriting the expander and the devectorizer. And these things are just 80% crap. Um because they're so old. So. Pretty good. Yeah. Trying to spec up a little bit. And yeah I'll get minigen passing all the tests. And then I'll port the optimizer stuff back to minigen, now that... the path we're doing that. Um. What else in UOp specs? Oh, we deleted VCONST. Actually delete VCONST more.

##### **Wozeparrot** [[00:13:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=785)]
More cleanly.

##### **Geohot** [[00:13:07](https://www.youtube.com/watch?v=s0VinPJFDeI&t=787)]
Um. VCONST is just stacked const. Uh yeah we shouldn't do that. Every time you think. Oh I'm going to be clever. I'm going to save a few things. Don't save a few things. It's not worth it. Uh just it's not. It's not O of N. The difference between const and VCONST is not really O of N. Because you're still constructing that. Does it really matter if you're constructing a Python tuple versus constructing a bunch of UOps. Yeah but the Python tuple is faster. Yeah it's an optimization. Optimizations are always a bad idea.

##### **Geohot** [[00:13:37](https://www.youtube.com/watch?v=s0VinPJFDeI&t=817)]
Always a bad idea.

##### **Geohot** [[00:13:38](https://www.youtube.com/watch?v=s0VinPJFDeI&t=818)]
Never want them. Oh that guy who submitted like 10 AI PRs. He wrote a blog post about how, "As a social experiment I spammed lots of people with AI PRs, and then I pissed them off, and I'm cool." Yeah, you'll fit right in in San Francisco.

##### **Chenyu** [[00:13:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=838)]
You can link the blog.

##### **Geohot** [[00:14:00](https://www.youtube.com/watch?v=s0VinPJFDeI&t=840)]
What? You can link the blog. Yeah. Um. I don't know. I don't think we should give this guy any more attention. But.

##### **Geohot** [[00:14:17](https://www.youtube.com/watch?v=s0VinPJFDeI&t=857)]
You know, just important to be aggressive against any AI stuff. He's trying to, like, market his... It's like Cluey. He's trying to market his... Keep AI PRs off of your thing. Prevent people like me from doing what I did. I'm like, no, I'm just going to ban you from GitHub and, like, just say you're a dick, and that's the end of that.

##### **Geohot** [[00:14:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=876)]
Yeah. Sad.

##### **Geohot** [[00:14:38](https://www.youtube.com/watch?v=s0VinPJFDeI&t=878)]
Yeah. Yeah, let's do UOp spec. So everyone also should look at the spec. The spec now lives in the tinygrad repo proper. Spec. Is it done? Is it done? It's never done. A living document. Oh, I added binary to the spec. So binary is just kind of like a... It's like a buffer, but the buffer doesn't actually live on the device. It just lives directly in the graph.

##### **Geohot** [[00:15:09](https://www.youtube.com/watch?v=s0VinPJFDeI&t=909)]
Yeah. Yeah. Kind of VCONST. It's not backend. But, you know.

##### **Geohot** [[00:15:16](https://www.youtube.com/watch?v=s0VinPJFDeI&t=916)]
You can use it like VCONST. It shouldn't really be a... It's like a constant. And maybe binary is even the wrong word. When you have, like, constant memory in GPU, it's something like binary. Like, that's if you want to put, like, a lookup table in there

##### **Geohot** [[00:15:33](https://www.youtube.com/watch?v=s0VinPJFDeI&t=933)]
and not have it actually go to memory. If a lot of GPUs basically support something like this. You can also use it to store the binary for the... Like, programs that run on the GPU.

##### **Geohot** [[00:15:47](https://www.youtube.com/watch?v=s0VinPJFDeI&t=947)]
Like const, it doesn't have a device.

##### **Geohot** [[00:15:50](https://www.youtube.com/watch?v=s0VinPJFDeI&t=950)]
It's like a... Like a deviceless buffer that lives in the graph. Cool. Everyone take a look at the new spec.

##### **Geohot** [[00:16:03](https://www.youtube.com/watch?v=s0VinPJFDeI&t=963)]
Oh, yeah. Also, I'll talk briefly about replicated. Replicated is the answer to multi. But I don't have it all figured out yet. But multi marks the... Okay, so multi... the multi kind of buffer. Multi right now is used to mark that something is sharded across devices. It actually should be the other way around. Sharded is implicit. If you have four devices, it implicitly shards across the devices. Think about, like, your HBM memory in your MI300, right? Like, there's eight banks of memory. And everything is implicitly sharded across those banks. So, the sharding is implicit. The stranger thing is replicated. So, replicated just means you want to store multiple copies of this tensor

##### **Geohot** [[00:16:59](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1019)]
along this axis in some sharded thing.

##### **Geohot** [[00:17:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1025)]
Yeah, and the replicated, actually, it's not just for... It's not just for multi. I really want to make sure that this replicated also works for there's a lot of patterns, low-level in kernels, where what you basically do is you, like, okay, think about, like, the normal globals, locals, registers map. You store from globals to locals, and then you load from locals multiple times into registers. That's a... Right, you load the same value. So, the same value is loaded multiple times all at once into registers in order to, like, bring memory locality. Yeah, that's the same replicated op.

##### **Geohot** [[00:17:47](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1067)]
That's where multi eventually goes.

##### **Chenyu** [[00:17:52](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1072)]
I don't get it, but, I mean... Yeah.

##### **Geohot** [[00:17:56](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1076)]
I wish it was more clear, but, yeah. Okay, this week I'm going to work on adding address space, continuing with minigen. Address space is just like device. It has a bunch of production rules.

##### **Chenyu** [[00:18:08](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1088)]
Yeah. Sounds good. Moving on.

##### **Chrism** [[00:18:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1092)]
Yeah.

##### **Chrism** [[00:18:15](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1095)]
I think that wasn't really

##### **Chrism** [[00:18:16](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1096)]
any major changes to arch. Just some sort of cleanups. So, CL, now you put the device extensions in there so that we can actually know, like, which... Like, if you support FP16 rather than saying, like, oh, if you're on a Mac, then you probably don't, and if you're on Linux, then you probably do. We can actually properly query that, which is good.

##### **Chenyu** [[00:18:38](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1118)]
Did you update the CI with that?

##### **Chrism** [[00:18:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1121)]
I updated `is_dtype_supported`, so therefore,

##### **Chrism** [[00:18:43](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1123)]
it should run those tests.

##### **Qazalin** [[00:18:48](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1128)]
Yeah.

##### **Chenyu** [[00:18:51](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1131)]
I think there was one open issue for at least one that complained about this. Oh, right. I don't know if it was, like, for CL or, I guess, certain backends who don't want to make the assumption because they're pushing it and they don't know something.

##### **Geohot** [[00:19:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1145)]
Yeah, yeah. So, are you having a way

##### **Geohot** [[00:19:07](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1147)]
to explicitly say that?

##### **Chrism** [[00:19:09](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1149)]
Yeah. Yeah. It is one thing, like, for Metal, with, like, hard-coding, it was, like, if CI, because the CI runners don't support FP16, maybe, that is now properly checked based on the GPU family version or whatever they call it.

##### **Geohot** [[00:19:31](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1171)]
Every test that's, like, based on slower CI, we should probably just delete.

##### **Chrism** [[00:19:35](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1175)]
Yeah. No, I really want to remove all the checks. Yeah, yeah.

##### **Geohot** [[00:19:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1181)]
I don't, because I don't think the LLVM tests will pass on my computer.

##### **Qazalin** [[00:19:45](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1185)]
Okay.

##### **Chrism** [[00:19:46](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1186)]
I will keep looking at that. Oh, yeah. LLVM has a little interesting thing where it's like, okay, like, you're on x86 and you don't have the FP16 support based on, like, the CPU extension. And so, we probably need to switch arch to use some sort of CPUID check to see which extensions you support.

##### **Geohot** [[00:20:08](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1208)]
What is LLVM doing? Like, LLVM just, like, emulating it?

##### **Chrism** [[00:20:13](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1213)]
It does, but it calls LLVM. Oh, okay. Yeah.

##### **Geohot** [[00:20:15](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1215)]
Can we just make CALL work?

##### **Chrism** [[00:20:17](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1217)]
Uh, yeah.

##### **Geohot** [[00:20:18](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1218)]
Yeah, let's do that.

##### **Chrism** [[00:20:18](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1218)]
Okay.

##### **Geohot** [[00:20:20](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1220)]
Um,

##### **Chrism** [[00:20:22](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1222)]
yeah, so that's, that's, Harold,

##### **Geohot** [[00:20:24](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1224)]
Harold posted something about, like, we should just make CALL work. Yeah.

##### **Chrism** [[00:20:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1227)]
Yeah, I saw it, I saw it, the adage that you posted, but,

##### **Geohot** [[00:20:30](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1230)]
you can totally make your loader just work for it. Yeah. You can just do that. That's currently working. Yeah, yeah, yeah. And if for some reason that's a problem, AI would do a great job at that.

##### **Chrism** [[00:20:40](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1240)]
Um, okay, anyway, uh, the other thing is some dtype changes, so, yeah, I mentioned a little bit of this, but I just want to get rid of `is_dtype_supported` entirely without all of the renderer. Um, so instead of having these dtypes imported and you pass, like, the target string, uh, instead, you'll, you'll, you can just call, like, `supported_dtypes`, uh, as a function on the renderer, and it gives you a set of the supported dtypes. Um, and that's nice, because then the renderer will be instantiated, um, and so we can actually, like, check based on the arch and say, okay, you know,

##### **Chrism** [[00:21:13](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1273)]
we don't have to say,

##### **Chrism** [[00:21:19](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1279)]
yeah,

##### **Chrism** [[00:21:20](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1280)]
in CI, we know we have, uh,

##### **Chrism** [[00:21:22](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1282)]
SM35, but we're, we're assuming that no one on the planet is still using SM35, uh, who isn't in CI,

##### **Geohot** [[00:21:30](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1290)]
but,

##### **Geohot** [[00:21:30](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1290)]
well, that's, uh, yeah, we may want to move,

##### **Geohot** [[00:21:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1296)]
I'd love to see SASS in, uh, kind of like the AMD emulator.

##### **Chrism** [[00:21:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1301)]
Yeah. That would be, that would be, yeah, I looked a little bit at this, but I looked it up, but it's just the other thing.

##### **Geohot** [[00:21:47](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1307)]
So if someone wants that project, that's, that's, uh, if you could replace, uh, GPU Ocelot with, uh, a SASS emulator on, like, something that's going to stay supported for a while, like, NIR.

##### **Chrism** [[00:22:00](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1320)]
Yeah, you don't have to go NIR, um, GPU Ocelot to, like, something in their build script and not getting what they need anymore.

##### **Geohot** [[00:22:08](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1328)]
Yeah, yeah, but it's also, that's not even, like, at the lowest level,

##### **Geohot** [[00:22:10](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1330)]
right? I'm just going to do it with the SASS.

##### **Chrism** [[00:22:15](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1335)]
Yeah, that would definitely be nice.

##### **Geohot** [[00:22:19](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1339)]
Uh,

##### **Chenyu** [[00:22:21](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1341)]
uh, environment variables for dtype, just check open issues. I think there are, I think, a few that mention this, and just make sure your change will cover all their needs and you can close them. Yeah, yeah. There are a bunch of, like, people complaining, like, some version doesn't support something, like, dtype,

##### **Chrism** [[00:22:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1361)]
and the error message was bad, or something like that. Yeah, I would believe that. The other thing that I removed was the dtype fallback in ONNX. This didn't regress anything for, like, our biggest ONNX consumer, which is openpilot, but basically, like, you just get emulated support if you're loading an ONNX model for a dtype that you don't support. I don't know, like, maybe there should be some tool that allows you to, like, easily convert the stuff so that you can convert your model weights, but that seems like something that someone else can write.

##### **Geohot** [[00:23:16](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1396)]
Yeah, yeah, I don't think so. I'd rather just emulate it and push it all the way to the bottom, because then that becomes speed and not, like, different.

##### **Chenyu** [[00:23:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1406)]
Is that logged somewhere? If my dtype is being emulated, some debug level should show that? I think that's it.

##### **Geohot** [[00:23:34](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1414)]
Yeah, probably in debug you should show, like, if you're, like, hitting some bad emulated path.

##### **Chenyu** [[00:23:39](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1419)]
Because I think the workflow for anyone that's debugging something probably starts with `DEBUG=2`. Yeah,

##### **Geohot** [[00:23:46](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1426)]
I don't think that should be too much spam. Yeah, the emulated dtype thing doesn't actually support, but, yeah, I'd much rather deal with that at a lower level so everything's the same.

##### **Chrism** [[00:23:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1438)]
That's an easy change. But, yeah, I think the next thing to work on is, like, I tried a little, I didn't really go through all the tests, you know, yet, but I did a little bit of stuff for CI to try and make it a little bit faster, just so we're not, I think the less stuff we rely on from apt the better. And so, I think I made it a little bit faster, but the real fix is to go in and find all the tests that we don't care about having and to

##### **Chenyu** [[00:24:29](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1469)]
If you are really into this, I was briefly thinking about this this morning. Oh, I made CI 10 seconds faster. You can try having an LLM go through kind of the ripple failure in the past, I don't know, six months, and if any test that has been there more than six months and never breaks or like, give me some judgment, but I can imagine there are some duplicated stuff that we can

##### **Chrism** [[00:24:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1498)]
just remove. And I think also, like, there's this thing where it's just like, you mentioned this, we're kind of testing at the wrong layer here, although I don't know if we totally have the infrastructure yet to be able to move everything to test it.

##### **Geohot** [[00:25:10](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1510)]
The first thing I would do when you redo the test is, I went too aggressive with this, just merge null and unit all into unit, and then unit are things that only run on one device, and then backend are things that run on other devices, and then we could, like, do more refactoring now. The other

##### **Chrism** [[00:25:23](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1523)]
thing that would probably be nice is if we had one, rather than having this `test.yml` file, we have 50 different jobs, and then each one has a little different set of things.

##### **Geohot** [[00:25:35](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1535)]
Yeah, we got to unify all that. We got to shrink this as a file. All right, before we get to, before we get to, to Wozeparrot, Qazalin, and Nimlgen, I posted in MLPerf LLaMA 405B, kind of, you know, the deliverable for your next sprint. I want to see a full 405B correct train, I want to see faster 8B training, and I want to see 8B training across both machines. So this is the remote team right now is the AMD contract team.

##### **Geohot** [[00:26:13](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1573)]
Those are kind of three goals for that. Yeah.

##### **Qazalin** [[00:26:23](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1583)]
Okay.

##### **Geohot** [[00:26:25](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1585)]
Sounds good. All right. HCQ2? Yeah,

##### **Nimlgen** [[00:26:34](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1594)]
so,

##### **Nimlgen** [[00:26:35](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1595)]
um, I have some implementation of HCQ2 in master. So it works for, it doesn't work for multi-GPUs, but it supports graph and runtime, and it shares most of the passes. So currently I'm just shuffling and just removing patch and making it a bit nicer.

##### **Geohot** [[00:27:07](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1627)]
Yeah, so. And we, uh, can we boot all the GPUs at once? Um,

##### **Geohot** [[00:27:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1646)]
what's it going to take to be able to do that? To, like, use the HCQ2 infrastructure in order to, uh, yeah, pretty much just like, like, it's a kernel. It's the boot kernel, and the boot kernel is broadcasted across, runs across the six GPUs.

##### **Geohot** [[00:27:44](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1664)]
Yeah, um, no, we probably can do that.

##### **Nimlgen** [[00:27:54](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1674)]
I mean, still, inside this kernel, you will have, like, six stores or something like that, right?

##### **Geohot** [[00:28:00](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1680)]
Uh, well, I wouldn't have six stores, what I would have is, I mean, you could do six stores, but you could also just have the kernel be, like, running on six threads.

##### **Geohot** [[00:28:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1692)]
Yeah.

##### **Geohot** [[00:28:13](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1693)]
Right? Like, it's just, it's some C... Yeah,

##### **Nimlgen** [[00:28:15](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1695)]
yeah, yeah, that's, that's possible. Yeah. Just, just, uh, like, range on top of the whole boot.

##### **Geohot** [[00:28:22](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1702)]
Exactly.

##### **Nimlgen** [[00:28:22](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1702)]
Yeah.

##### **Geohot** [[00:28:23](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1703)]
I want it to be, I want it to literally be range on top of the boot. Um, because the problem with putting six stores in is now you're in O of N scaling, and we need O of 1 scaling, right? Like, whatever your, whatever, whatever stuff we're writing now to boot the GPUs, um, again, when we're talking about one or six, it doesn't really matter that much. Because, like, okay, it's not that slow to boot six GPUs, but once we're booting 600, that's a huge difference.

##### **Chenyu** [[00:28:54](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1734)]
600.

##### **Qazalin** [[00:28:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1738)]
Yeah,

##### **Geohot** [[00:28:59](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1739)]
so we have to start thinking about how to do O of 1 to boot all the GPUs and not all that. And then this should

##### **Geohot** [[00:29:09](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1749)]
also Yeah, I mean,

##### **Nimlgen** [[00:29:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1752)]
yeah. I mean, still a lot of work for, I know, so just to land these HCQ2 changes and not break, um, I think performance for, actually, the, like, because of the scheduling all these rewrite rules is just 50% slower. But until graph, so actually each kernel to compile each kernel is 50% slower. Like if you're running tests, so you compile

##### **Geohot** [[00:29:44](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1784)]
them slower. Oh, you mean to like build the thing?

##### **Nimlgen** [[00:29:47](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1787)]
No, I mean, yeah, yeah. So just all these rewrites, you just run like tests, like it's 50% slower.

##### **Geohot** [[00:29:56](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1796)]
Yeah, yeah. I mean, we should figure out if this hotspot gets a bit slower, gets a bit slower.

##### **Nimlgen** [[00:30:04](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1804)]
Yeah. So still, like, multi-GPU is to do, but that's USB GPU. But actually, for USB GPU, the blocker is, I want to rip out the, like, non-custom firmware things and caches. They are pretty annoying.

##### **Geohot** [[00:30:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1826)]
Oh, you mean all the ones that work with, like, the stock firmware?

##### **Nimlgen** [[00:30:30](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1830)]
Yeah, yeah, yeah.

##### **Geohot** [[00:30:31](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1831)]
Yeah, we can rip all that out. That's fine. Yeah, no, hopefully the custom firmware, it's very clear what everything is. Like, on the other one, it was, like, a little bit, oh, I don't know what this says, I don't know what this says. Like, now with the custom firmware, it's like, boom, you have some SRAM on the device, you have these two ways to do it, and that's it.

##### **Geohot** [[00:30:55](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1855)]
Yeah,

##### **Nimlgen** [[00:31:00](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1860)]
maybe I can even do, like, the multi-machine training on HCQ2.

##### **Geohot** [[00:31:06](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1866)]
Oh, yeah, I think we should only do it for HCQ2. I don't think we should try to make it work with the old stuff. I think, like, that's the training across the 16 MI300, MI350s is the target of HCQ2.

##### **Geohot** [[00:31:21](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1881)]
And hopefully we can boot all 16 at once.

##### **Nimlgen** [[00:31:33](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1893)]
Yeah. I think we can. I'm pretty happy with the way I can build these launcher programs. I think, yeah, that's definitely possible. Yeah.

##### **Geohot** [[00:31:48](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1908)]
Anything else?

##### **Nimlgen** [[00:31:52](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1912)]
Um, no. I think, yeah, this week I'll still focus on HCQ2. I'll try to do some. I don't know if I'll be able to merge it and make it default. But I think it will be ready, like, graph, multi-GPUs, all these things.

##### **Geohot** [[00:32:17](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1937)]
Yeah, take your time. Make sure you do it right. If you feel like something's being implemented wrong, slow down, make sure it's implemented right.

##### **Nimlgen** [[00:32:25](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1945)]
Yeah.

##### **Geohot** [[00:32:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1946)]
Um, but, yeah, no, I think, yeah, let's, yeah, let's delete patch and switch that to index/store/assign, have binary now.

##### **Qazalin** [[00:32:33](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1953)]
Um,

##### **Geohot** [[00:32:34](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1954)]
and now, like, hopefully, it's clear. Like, when you have binary and you have, like, a store to it, a store and an AFTER, you can do a rewrite of that store and AFTER to change binary. Like, you don't need that device to do that, you, yeah.

##### **Nimlgen** [[00:32:53](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1973)]
Yeah, that's already done. I mean, like, the const folding, yeah.

##### **Geohot** [[00:32:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1978)]
Yeah, that's just a rewrite rule that, that, that will, uh, Yeah, yeah, yeah. do the pass for you, basically. Um, and then you don't have to worry about what device that's on.

##### **Nimlgen** [[00:33:08](https://www.youtube.com/watch?v=s0VinPJFDeI&t=1988)]
Yeah, so, uh, yeah, I think this thing I'll probably merge today and remove patch. Uh, but still, yeah, it's a lot of cleanups to, to do.

##### **Geohot** [[00:33:20](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2000)]
Sounds good.

##### **Geohot** [[00:33:24](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2004)]
Let's move on to this.

##### **Qazalin** [[00:33:28](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2008)]
Last week, I worked on getting better tools for scheduler. So, exposing stuff like what's fused and, like, tracing the buffers. That helped with getting speedups on Qwen. I'm transitioning to LLaMA now. Um, LLaMA regressed from, uh, upgrading ROCm. I think we should, uh, revert back to ROCm 7.1 unless there's a good reason we should use the new version. Uh, it regressed pretty badly. And

##### **Qazalin** [[00:34:03](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2043)]
there's a couple of regressions. First, it doesn't beam anymore because new ROCm just hangs compiling some kernels.

##### **Geohot** [[00:34:11](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2051)]
Yeah.

##### **Geohot** [[00:34:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2052)]
Oh, well, that sounds like a bigger problem. I don't think the solution here is to revert ROCm. I think the solution here is to figure out why can't we just handle that hang.

##### **Qazalin** [[00:34:22](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2062)]
uh, we can, because we call C. You have to like put it on a thread or something.

##### **Geohot** [[00:34:28](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2068)]
Actually killable.

##### **Qazalin** [[00:34:30](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2070)]
Yeah.

##### **Geohot** [[00:34:31](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2071)]
We should fix that. We shouldn't downgrade ROCm. Like, if there's regressions in the LLVM of ROCm, that's different. But if there's just it hangs sometimes now, then we just have to handle this. So like, because other people have that.

##### **Qazalin** [[00:34:44](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2084)]
What? There's also a performance regression.

##### **Qazalin** [[00:34:49](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2089)]
Performance is very bad. Our GEMM went from about 2.8 petaflops to 900 teraflops.

##### **Geohot** [[00:34:59](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2099)]
Same exact code?

##### **Qazalin** [[00:35:01](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2101)]
Same exact code. I am completely shocked.

##### **Geohot** [[00:35:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2105)]
Well, all right. Fine. Revert it. Yeah. Yeah. Just downgrade it. Yeah. Okay. Never mind.

##### **Qazalin** [[00:35:10](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2110)]
Yeah. Yeah.

##### **Qazalin** [[00:35:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2112)]
I merged something to like make it faster so it's not too painful. So it's less embarrassing, but I'm going to revert it. Like, honestly, it's not worth it.

##### **Geohot** [[00:35:20](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2120)]
Yeah. I mean, I also want to start to move those things. The other project I want you to work on is moving those things out of custom C and move them into like the lowest level of UOps. Or are those kernels all in assembly?

##### **Qazalin** [[00:35:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2136)]
Our kernels are mostly in C.

##### **Geohot** [[00:35:38](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2138)]
Okay.

##### **Qazalin** [[00:35:40](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2140)]
Yes.

##### **Geohot** [[00:35:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2141)]
Do they have assembly or not?

##### **Qazalin** [[00:35:44](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2144)]
We do have one assembly, the GEMM one, the BF16 GEMM. It's used a little bit in the model, but most are in C.

##### **Geohot** [[00:35:52](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2152)]
I really want to try to move them to UOps.

##### **Geohot** [[00:35:57](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2157)]
Hmm.

##### **Geohot** [[00:35:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2158)]
Like with all of these LLaMA speedups, I don't want you or an agent to start just adding in tons of like HIP code. I want it to be moved to like the lowest level of UOps. So we're within the UOp spec and then the UOp spec is lowered and compiled. Like, that was the problem with all the custom kernels that we used for MLPerf submission. We reverted because it's just random HIP code and we can't really reason about that. You have to redo that, but properly in UOps. And then, yeah, get the tooling to work with an agent. We need to push this below two hours.

##### **Qazalin** [[00:36:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2196)]
First UOps and then work on the one or two hours?

##### **Geohot** [[00:36:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2201)]
Yeah, yeah, I would say, like, if you can move it to UOps without slowing it down, that's a good first step.

##### **Qazalin** [[00:36:53](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2213)]
I'll try it this week, see how it goes.

##### **Geohot** [[00:37:00](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2220)]
Yeah, no, I think that gives you a pretty good long-term goal. I think it's going to be like two sprints. I'm hoping in, like, a month you can have LLaMA under two hours.

##### **Geohot** [[00:37:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2232)]
Yeah. Anything else?

##### **Qazalin** [[00:37:24](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2244)]
I think that's it.

##### **Geohot** [[00:37:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2247)]
Oh, so when you use this flash infer, does this do...

##### **Geohot** [[00:37:35](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2255)]
I see. OK, cool. Yeah, I mean, I see a lot of these.

##### **Qazalin** [[00:37:38](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2258)]
A bunch of hand-coded kernels from NVIDIA.

##### **Geohot** [[00:37:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2261)]
Yeah, like, I see a lot of these kernels are written in HIP. Like, can we write these things in UOps?

##### **Qazalin** [[00:37:49](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2269)]
Yeah, those are the kernels. Yeah.

##### **Geohot** [[00:37:52](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2272)]
For every kernel, like, is there any reason we can't write it in UOps? Like, I think this is going to be maybe even your project sort of for the rest of the year to figure out how to find the highest performance kernels on things and then move them as much up the stack as we possibly can. Like, move them to the highest level UOp representation that we possibly can. That gets all the, like, memory stuff right. And I think we can do, because none of these have asm. Like, all these custom kernels, that's like the one that's making Qwen 16% faster. That's not assembly. We should totally be able to write that in UOps and output it.

##### **Qazalin** [[00:38:33](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2313)]
Agents are very bad at writing UOps, by the way.

##### **Geohot** [[00:38:37](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2317)]
Why?

##### **Qazalin** [[00:38:38](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2318)]
I tried. I don't know. Like, GPT-5.5 spent an hour trying to port one of these kernels into UOps and kept getting like linearizer errors. This can't exist backward.

##### **Geohot** [[00:38:55](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2335)]
All right. Well, it sounds like you got to improve the errors.

##### **Qazalin** [[00:38:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2338)]
Yeah. I know. But it is a big investment.

##### **Geohot** [[00:39:03](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2343)]
Yes. This is this is worthwhile. I mean, these errors need to be improved for humans and agents alike.

##### **Chenyu** [[00:39:09](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2349)]
Yeah, I think it might be interesting to try to semi-formalize the thing you just described, that you have a problem in hand and somehow you cannot get agents to do it, because I think that's something people would be

##### **Chenyu** [[00:39:23](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2363)]
interested to try.

##### **Chenyu** [[00:39:24](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2364)]
It's very hard to say it doesn't work just because it doesn't work for me. It's very different. And for example, what you just described, I'm interested to try, but I don't know what specific thing should I be looking. It would be nice if you have some examples saying, this is the code, this is the thing I wanted to translate into UOp, and maybe someone would be interested to figure it out.

##### **Geohot** [[00:39:50](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2390)]
Yeah, yeah, if you could post the prompt that doesn't work, and then we can figure out why it doesn't work.

##### **Chenyu** [[00:39:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2398)]
Maybe not even the prompt, maybe some of these examples, but standalone and something I can run. That would be nice.

##### **Geohot** [[00:40:04](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2404)]
Something small that that shows like, yeah, and then if our errors are incomprehensible, they're incomprehensible to humans also. If an agent can't figure it out, a human can't figure it out. So we need to improve the errors and we need to either need to improve the error or make that error just not be possible to happen. Like, like, you know, you have to split errors into like, okay, the user is actually holding it wrong or the library is not processing it correctly.

##### **Chenyu** [[00:40:32](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2432)]
It's very possible that we still have something missing in our current representation or our algorithm. Both are very likely. Yeah. Having these as kind of our own eval set for how we use agents would be nice.

##### **Qazalin** [[00:40:49](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2449)]
Yeah. I'm also like thinking about examples that I'm giving to agents. The only example that we have right now is the Flash Attention one. But I think there's like an opportunity for agents to write something in Tensor level and then see it through the compilation. Yeah.

##### **Chenyu** [[00:41:08](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2468)]
Yeah. It's always nice to broaden those, but I think it's still nice to have something that we know the answer of. Yeah. Examples for GEMM and Flash Attention are valuable because we already know a generation of engineers put lots of time in it and the output is probably the best we could get.

##### **Geohot** [[00:41:28](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2488)]
Part of the problem with that Flash Attention that I wrote is like, I don't really know what the performance should be versus these MI350 Flash Attention kernels. We know what the performance should be. Like, we've submitted MLPerf now with these things. So now if we can write UOp ones that beat those, that's really valuable because we know that, you know, not just engineers put time into writing that Flash Attention, but we put time into finding that Flash Attention and making it work for our use case. We have a real in-context benchmark.

##### **Geohot** [[00:42:09](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2529)]
And I will call my agent smarter.

##### **Geohot** [[00:42:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2532)]
Mmm.

##### **Geohot** [[00:42:13](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2533)]
Okay,

##### **Geohot** [[00:42:14](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2534)]
anyway. Sounds good. Anything else?

##### **Qazalin** [[00:42:22](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2542)]
LLaMA.

##### **Wozeparrot** [[00:42:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2546)]
I did a bunch of cleanups and fixes for regressions last week, mostly because machines were down like two days last week.

##### **Geohot** [[00:42:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2556)]
Everything should be fixed and very stable now. I did some training runs.

##### **Wozeparrot** [[00:42:42](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2562)]
I realized that they were with old cache. That's why my runs worked and Qazalin's didn't. Hmm. But

##### **Geohot** [[00:42:53](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2573)]
I saw four. Okay, so.

##### **Wozeparrot** [[00:42:57](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2577)]
No, because I just ran dev run for these runs.

##### **Chenyu** [[00:43:02](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2582)]
So if I go and run from master, does everything work?

##### **Qazalin** [[00:43:07](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2587)]
You have to change your ROCm path to 7.1. Once I did that, it passed. Yeah.

##### **Chenyu** [[00:43:14](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2594)]
Oh, is that documented somewhere?

##### **Qazalin** [[00:43:17](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2597)]
It's in the channel. You can use mine, and I installed ROCm 7.1 on both machines.

##### **Chenyu** [[00:43:24](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2604)]
That's why, for our MLPerf stuff, I think they will assign some review thingy for the next few weeks.

##### **Wozeparrot** [[00:43:32](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2612)]
Yeah. Should I do the reviews?

##### **Chenyu** [[00:43:34](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2614)]
Depends on how big the review is. If it's like we have one submission, we review some other people's with one submission, I can do that. If not, I will complain because this last time we submitted one and we need to review like three. I was pretty not happy to take it.

##### **Wozeparrot** [[00:43:51](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2631)]
Okay, but I should do the meetings too. Yeah.

##### **Chenyu** [[00:43:55](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2635)]
Oh, sure. Up to you if you're interested. I usually just join and mute myself and nothing really happened.

##### **Qazalin** [[00:44:04](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2644)]
Okay,

##### **Wozeparrot** [[00:44:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2645)]
I'll do the meetings.

##### **Qazalin** [[00:44:06](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2646)]
Okay. Yeah. Uh,

##### **Chenyu** [[00:44:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2652)]
your email is the tiny

##### **Geohot** [[00:44:14](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2654)]
I know. I'm just trying that. What? This invite has expired. What? Do you have access to this? I do. Okay, we'll go through it later. I shouldn't talk

##### **Geohot** [[00:44:25](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2665)]
about it at the

##### **Geohot** [[00:44:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2666)]
meeting. Okay.

##### **Qazalin** [[00:44:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2667)]
Yeah. Uh,

##### **Chenyu** [[00:44:29](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2669)]
Do we cut a release this week? MLPerf submitted, there's no reason to delay. We are going to merge the S2.

##### **Geohot** [[00:44:37](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2677)]
Yes.

##### **Chenyu** [[00:44:39](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2679)]
I forgot who complained.

##### **Chrism** [[00:44:42](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2682)]
Or just random people.

##### **Chrism** [[00:44:44](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2684)]
I don't think it's that big of a deal. But I just think it's just nice to have. Yeah, no,

##### **Geohot** [[00:44:48](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2688)]
Yeah, I definitely want to release this week.

##### **Wozeparrot** [[00:44:50](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2690)]
Okay, I'll tag a release this week. Great. Then just tracking down some 405B memory regressions.

##### **Geohot** [[00:45:01](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2701)]
Yeah, memory regressions. Yeah, when you tag the release, I want you to check, make sure all that AMD stuff ships.

##### **Geohot** [[00:45:13](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2713)]
I'm hoping to have 8B MP trained this week.

##### **Qazalin** [[00:45:20](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2720)]
Okay.

##### **Chenyu** [[00:45:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2726)]
Bounties, issues. Comma happiness. Is Comma happy?

##### **Chrism** [[00:45:30](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2730)]
I think so. I mean, we fixed their LLVM issue, and so they bumped again

##### **Chrism** [[00:45:37](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2737)]
today.

##### **Geohot** [[00:45:40](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2740)]
Oh, do we have any pending item on app?

##### **Qazalin** [[00:45:54](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2754)]
I think so.

##### **Chenyu** [[00:45:56](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2756)]
Or do you want to do you want to say anything? Anything we are not reviewing?

##### **Geohot** [[00:46:01](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2761)]
Oh, yeah. Did I give you feedback on the shard thing? We don't want to shard like that.

##### **B1tg** [[00:46:08](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2768)]
Okay. My sharded master is layer-wise. That's the norm default behavior.

##### **Geohot** [[00:46:19](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2779)]
Oh, yeah. No, I mean, the problem with layer-wise is it's not going to speed up at all.

##### **B1tg** [[00:46:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2786)]
Yeah, I know you want the tensor-wise shard.

##### **Qazalin** [[00:46:30](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2790)]
Okay.

##### **Geohot** [[00:46:31](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2791)]
It should be easy, though. Tensor-wise shard should be easy in tinygrad. It's all like supported. You just need to do a little bit of work in the GGUF loader to make sure you shard them early enough.

##### **B1tg** [[00:46:42](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2802)]
I tested with the older LLaMA example in our tinygrad codebase. With sharded things, it makes the speed slower.

##### **Geohot** [[00:46:57](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2817)]
I shouldn't be true. I think there might

##### **Geohot** [[00:47:02](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2822)]
be regressions, but it definitely used to be faster.

##### **B1tg** [[00:47:06](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2826)]
Okay. I think in our use case, our batch equals one. So we don't trigger the bigger matrix multiply. So our bigger calculation is a GEMV, not the matrix multiply. So the shard overhead may make things slow.

##### **Geohot** [[00:47:43](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2863)]
No way. For something like Kimi, there's no way that's true. For something that's big, I can't imagine what like there has to be some kind of bug, because these matrices are so big and you're totally just memory bound that the sync overhead should be small. I mean, if it is slower, we have all the tooling to look at this now, too. Like, I would write a microbenchmark. Just do some one-sharded GGUF GEMV and look at it in viz and figure out why it's slower, because we definitely want to shard on the matrix. I expect almost linear speed up. Certainly going to two GPUs, I expect linear speed up, but even going to four, I still expect to get like 80% of max. If it's like 50 tokens per second on one, I expect it to be like 98 on two and like 180 on four.

##### **Chenyu** [[00:48:40](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2920)]
60.

##### **Geohot** [[00:48:42](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2922)]
Well, so this Kimi is 33, but this is the layer-wise sharding. 80%. Yeah, yeah, something, but I think that we should be able to get over 100 tokens per second with matrix sharding across four. You have to be a little careful how you do the matrix sharding, though, because there's like wrong ways to do it that will be slower. But if you look at how we did it in LLaMA, that should be faster. And if for some reason, it's not faster, something regressed because that definitely used to be faster.

##### **Geohot** [[00:49:15](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2955)]
I didn't have it in.

##### **B1tg** [[00:49:21](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2961)]
OK, llama.cpp also supports the experimental tensor-wise shard, and they posted some results.

##### **Geohot** [[00:49:37](https://www.youtube.com/watch?v=s0VinPJFDeI&t=2977)]
Oh, wow. Yeah, it majorly regressed. I mean, you can see it in the benchmark here that it majorly regressed. It went down from its 40 tokens per second on one GPU and 21 tokens per second on four. Yeah, that's some regression. When did that happen? It would be nice

##### **Chenyu** [[00:50:03](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3003)]
to have a dashboard for that.

##### **Geohot** [[00:50:04](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3004)]
We do. Does it work? I don't know. Dashboard.

##### **B1tg** [[00:50:10](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3010)]
Oh, so the shard used to be faster.

##### **Geohot** [[00:50:14](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3014)]
Yeah, it used to be way faster. Oh, that was a little aggressive.

##### **Geohot** [[00:50:20](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3020)]
Right here. Yes.

##### **Qazalin** [[00:50:29](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3029)]
Looks very happy.

##### **Geohot** [[00:50:34](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3034)]
Yeah, I don't even know. Yes.

##### **Chenyu** [[00:50:37](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3037)]
Oh, yeah. It should. Yeah. Yeah, right. It should theoretically be faster and practically used to be faster. We probably regressed something.

##### **Geohot** [[00:50:45](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3045)]
Yeah, we got to. This is part of the test project. We got to move these tests. I don't want LLaMA 3 and GPT-2 anymore. Wow.

##### **Geohot** [[00:50:54](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3054)]
Yeah.

##### **Nimlgen** [[00:50:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3058)]
GPT-3 is nice.

##### **Geohot** [[00:50:59](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3059)]
Well, it's nice.

##### **Geohot** [[00:51:01](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3061)]
And you can do it.

##### **Chenyu** [[00:51:02](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3062)]
No, no, no, no. Old LLaMA especially. You cannot find weights anywhere now.

##### **Geohot** [[00:51:09](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3069)]
Yeah. The old crappy quantization. Like this is all gone. Let's just find the most modern. What are the most popular GGUFs on Hugging Face? Last seven days of trending. How do I get longer trending?

##### **Geohot** [[00:51:24](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3084)]
Well, what is this MiniCPM-sized LLM? I don't know.

##### **Geohot** [[00:51:40](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3100)]
Those are the ones people really use. BERT. Oh, little Qwen. Yeah.

##### **Geohot** [[00:51:49](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3109)]
Yeah, I told you. Thank you. All right.

##### **Geohot** [[00:51:51](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3111)]
All right. Yeah. No. Hugging Face doesn't show me the thing I want.

##### **Chenyu** [[00:52:00](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3120)]
Well, later. Yeah. Okay, finish the meeting. I don't think we probably have any more glaring issues.

##### **Wozeparrot** [[00:52:10](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3130)]
Oh, there's one people reporting bugs in rangeify.

##### **Chenyu** [[00:52:16](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3136)]
Or if someone will.

##### **Geohot** [[00:52:18](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3138)]
Is it an issue?

##### **Chenyu** [[00:52:19](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3139)]
Yeah, the comp backward hangs. Yeah. So I think this is a real bug. We can reproduce that only on GPU. So does it work on mine?

##### **Geohot** [[00:52:38](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3158)]
Maybe you need to import it.

##### **Qazalin** [[00:52:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3161)]
What? Oh. I don't even understand why that didn't work. OK.

##### **Geohot** [[00:52:48](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3168)]
Yeah, so.

##### **Geohot** [[00:52:49](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3169)]
I'm going to crash my computer. Yes. It worked.

##### **Chenyu** [[00:52:54](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3174)]
So that failed on my? That was on Mac?

##### **Geohot** [[00:52:57](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3177)]
OK.

##### **Chenyu** [[00:52:57](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3177)]
And I have weird result from OpenCL, but that's also on Mac. So I don't know. Maybe it's a Mac. OpenCL translates to Metal. Yeah. So maybe some issue with that. But I want things like that to be aware and probably should have a better error message. Well, I mean. I mean, it's hard if it's not.

##### **Geohot** [[00:53:19](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3199)]
It might just be a, yeah, like it's not failing on my machine. This might just be like a.

##### **Chenyu** [[00:53:25](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3205)]
Mac issue or unknown.

##### **Geohot** [[00:53:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3207)]
Well, yeah.

##### **Chenyu** [[00:53:29](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3209)]
Or maybe something undefined behavior.

##### **Geohot** [[00:53:30](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3210)]
No, no. It's probably this kernel. This kernel. This actually is a rangeify issue, right? Like, look at this kernel. None of these things are getting mapped to GPU global axes. This is all just look at that. So this is this is a problem kernel. I bet on Mac they should run that with `DEBUG=2` to see if this is actually the problem kernel.

##### **Wozeparrot** [[00:53:50](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3230)]
But like, look at this kernel. Is it an R kernel with a bunch of dims? Yes. Yes. They said it in the issue. They have that.

##### **Geohot** [[00:54:00](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3240)]
Yeah. Yeah.

##### **Qazalin** [[00:54:02](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3242)]
Yeah.

##### **Chenyu** [[00:54:03](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3243)]
Yeah.

##### **Geohot** [[00:54:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3245)]
It's a little bit of a problem kernel. Because it's not using the GPU. It's not using any sort of GPU speedups.

##### **Chenyu** [[00:54:12](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3252)]
Why would that crash my machine?

##### **Geohot** [[00:54:14](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3254)]
Well, just the Mac driver sucks. Okay.

##### **Qazalin** [[00:54:26](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3266)]
Cool.

##### **Chenyu** [[00:54:27](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3267)]
I also saw you have anything to say for the thing you were trying?

##### **Flata** [[00:54:33](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3273)]
Yeah.

##### **Flata** [[00:54:36](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3276)]
Yeah, I think I figured that out. I'm just working on my correctness check against the reference implementation. So I might use one of the TinyG3 machines, hopefully this week, so I can test out the full training load for Flux.

##### **Chenyu** [[00:54:53](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3293)]
Sounds good.

##### **Geohot** [[00:54:54](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3294)]
Feel free. No one uses TinyG3.

##### **Chenyu** [[00:54:58](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3298)]
Yeah, if you have issues with machines, just post somewhere, we will figure that out. Also, we have a PR for 70B LoRA.

##### **Geohot** [[00:55:11](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3311)]
We have a good one? I saw a bunch of like, now you get PRs, and you get AI copies of them, which is the good one.

##### **Wozeparrot** [[00:55:19](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3319)]
I reviewed this one slightly. Yeah, how do you like it? Somewhat OK. Yeah.

##### **Chenyu** [[00:55:25](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3325)]
Yeah. So Burton said, see if you just want to grant them machine. I don't know what's the, how do people figure out who is working on which big AMD machine, but I really want to try this.

##### **Geohot** [[00:55:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3341)]
Well, they should also be, AMD, I'm more OK with granting people AMD 1 and 2 right now. Those machines should be stable and good now. So all that instability should be gone. They replaced the GPUs entirely. AMD just replaced the entire GPU trays. You know, that was before AMD realized how much they liked us. So they gave us crappy GPUs in the beginning, but then they gave us good ones.

##### **Qazalin** [[00:56:03](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3363)]
Yeah.

##### **Chenyu** [[00:56:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3365)]
Then, Wozeparrot, can you just, if you are happy with that, can you just grant permission to the person?

##### **Wozeparrot** [[00:56:11](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3371)]
Yep.

##### **Geohot** [[00:56:13](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3373)]
I like this too, because yeah, it's another thing that we can compare to MLPerf.

##### **Chenyu** [[00:56:19](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3379)]
And this is also fast-ish, which is nice. I don't know how much we need to be careful about our dataset allocation, but hopefully. What do you mean dataset allocation? Because now each MLPerf has like one TB of data. Oh, yeah.

##### **Geohot** [[00:56:34](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3394)]
We have lots of hard drives. We don't want to.

##### **Wozeparrot** [[00:56:37](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3397)]
As far as I know, 70B data is not that big. It's pretty small.

##### **Chenyu** [[00:56:41](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3401)]
OK.

##### **Chenyu** [[00:56:42](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3402)]
That's even better.

##### **Geohot** [[00:56:43](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3403)]
I learned what LoRA was last week. I like LoRA. Simple.

##### **Chenyu** [[00:56:47](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3407)]
OK.

##### **Chenyu** [[00:56:48](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3408)]
So I'll leave that to you and just update the channel.

##### **Geohot** [[00:56:56](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3416)]
I think that's it. Would you want to do that, please? Oh.

##### **Chenyu** [[00:57:02](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3422)]
Oh.

##### **B1tg** [[00:57:04](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3424)]
OK. Cool.

##### **Geohot** [[00:57:05](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3425)]
Yeah. Just for one minute, I'll say, Comma gave us a big model, the CAFormer M36. Right now it runs at about 100 milliseconds. They say we need to get it to 33.

##### **Chenyu** [[00:57:20](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3440)]
Is that comparable FLOPS to the current thing, or a lot faster?

##### **Geohot** [[00:57:25](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3445)]
It's actually faster. So the current FLOPS for the current model is about 110. This one is already running at 150 GFLOPS. And if we want to get it fast enough, we have to get it up to 350. So I have a GEMM. So most of the GEMMs in there run at about 180. By hand-coding the GEMM in assembly, you can get it up to 310. If I find some magic trick to make it faster. The theoretical, so I can get the max ALU is 710. That's in theory what's doable. In practice, you're limited by the local memory. But if I can find some trick, I think 500 is actually doable.

##### **Geohot** [[00:58:15](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3495)]
If I can get around this one problem.

##### **Chenyu** [[00:58:17](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3497)]
Yeah.

##### **Geohot** [[00:58:19](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3499)]
So it is runnable if we get 500.

##### **Chenyu** [[00:58:24](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3504)]
Great. OK.

##### **Geohot** [[00:58:28](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3508)]
All good. I think that's it for today. Thank you, everyone. See you next week. Bye bye.

##### **Chenyu** [[00:58:33](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3513)]
Bye bye.

##### **Beohot** [[00:58:35](https://www.youtube.com/watch?v=s0VinPJFDeI&t=3515)]
Bye bye.
