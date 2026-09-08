# 2026-09-07 Meeting

### Meeting Agenda

**Time:** new meeting #36, 9/7 9am Monday San Diego time
- company update, Exa Box
- OptOps, ASSIGN, validate, x86 cleanups
- rangeify, CALL, CALLify
- CI infrastructure, GARM, Gitea, Incus
- LLaMA and GPT-OSS training
- HCQ2 and multi-machine training
- comma, RDNA3, GPU Ocelot bounty


### Audio

[Youtube Link](https://www.youtube.com/watch?v=ZvzpGOMjeF4)

### Highlights

- **[Exa Box Update](#geohot-000008)**: Using Chinese contractors for HVAC integration with two bids submitted; tiny corp profits on the computers themselves rather than doing specialist engineering work.

- **[OptOps Consolidation](#chenyu-000126)**: Extensive fuzzing fixed PADTO-related bugs; OptOps reduced to only four, with UPCAST, UNROLL, and LOCAL now unified as SPLIT, and NOLOCALS/WARP removed.

- **[GPT-6 for Bug Finding](#geohot-001029)**: GPT-6 excels at fuzzing and finding bugs (subtle race conditions in fast USB transfer path) but fails at spec work, simply making tests pass rather than fixing root causes.

- **[CALLify Progress](#geohot-001153)**: Spec is now correct after removing RETURNED; unbound BUFFERs can be inputs to CALL and local CALLs without becoming global BUFFERs, enabling proper optimization.

- **[BUFFER Type Definitions](#geohot-001703)**: Three BUFFER kinds formalized—unbound (no real backing, may be optimized out), bound (physical device location, cannot be memory-planned), and CALLify BUFFERs.

- **[CI Infrastructure Overhaul](#chrism-002437)**: Comma 3Xs removed from CI (all comma 4s with Chestnuts); GARM running on Gateway 2 for GitHub/Gitea runner management with Incus for resource pooling.

- **[GPT-OSS Training Speed](#wozeparrot-003710)**: Fastest run yet at 2h36m (700ms/step); compute time under 600ms with communications as the remaining bottleneck; ~10 minutes startup time.

- **[LLaMA Training Progress](#qazalin-004147)**: Latest time 1h53m (down from 1h55m); bottleneck is MXFP4 GEMM performance—NVIDIA achieves 60%+ MFU on the same shapes vs. tinygrad's current kernels.

- **[HCQ2 as Default](#nimlgen-004952)**: HCQ2 is now the default runtime with HCQ1 removed; everything is faster after the rewrite using a single compiled program, though all-to-all communication is still needed.

- **[GPU Ocelot Bounty](#geohot-010045)**: A working submission exists that passes tests and doesn't appear AI-generated; plan is to merge it into tinygrad/gpuocelot and update CI accordingly.


### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=0)]
Cool, let's get started. As usual, we'll start with the company update.

##### **Geohot** [[00:00:08](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=8)]
We're going to use Chinese contractors for the Exa Box. We have two people submitting bids. We're not HVAC specialists; we shouldn't be figuring out how to connect chillers to heat exchangers or whatever. We can just pay someone to do it. We should think of the Exa Box as making the profit on the computers.

It was funny watching Elliot Arledge build a four RTX PRO 6000 machine. It's not going to work. Those extenders don't work for signal integrity, and if you're using two power supplies, you can't connect the 12 volts, which is what those extenders are doing. I think that's good marketing for us. We sold a few more Pros. I think this was the same as last week: they're annoying to build, but they make money.

##### **Chenyu** [[00:01:21](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=81)]
Sounds good. Anything else?

##### **Geohot** [[00:01:23](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=83)]
No.

##### **Chenyu** [[00:01:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=86)]
Okay. Let's move on. First is my item. I ended up working on something that's not assigned because I saw George doing something around ASSIGN. I fuzzed a lot of OptOps because there were some bugs with PADTO. I think I fixed pretty much all of it, and it does a lot of random stuff now. It should be more stable and correct in general.

Also, I think between Chris, George, and me, we removed a bunch of OptOps. Now there are only four. UPCAST, UNROLL, and LOCAL are all just SPLIT now, and we no longer have WARP and NOLOCALS. I think we're good.

##### **Geohot** [[00:02:28](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=148)]
It's pretty clean. You changed it to SPLIT. Oh, I see. Yeah, that makes sense. No more UNROLL.

##### **Chenyu** [[00:02:45](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=165)]
I started with UNROLL being just UPCAST, then UPCAST and LOCAL being the same thing. The BEAM is slightly slower because, to match the previous space, the space is slightly bigger. But we never really revisited the space, so it is what it is. Previously, when we did the UNROLL and REDUCE thing, we reindexed from the first REDUCE. Now, to reach the previous REDUCE indexes, we need to have a bigger number.

##### **Geohot** [[00:03:37](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=217)]
In a similar vein, we have GROUP_REDUCE in AxisType, and that should just be deleted. Should UPCAST and UNROLL even still be in AxisType? There's almost even a question of whether REDUCE should be in AxisType.

##### **Chenyu** [[00:04:08](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=248)]
I didn't really think about this, but we don't even have a way to express multi-reduce doing weird things in that space, so it's unclear.

##### **Geohot** [[00:04:21](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=261)]
When you say multi-reduce, do you mean multiple reductions or a multi-device reduction?

##### **Chenyu** [[00:04:27](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=267)]
Multiple reductions in one kernel. You can do slightly different things in your upper REDUCE and your lower REDUCE.

##### **Geohot** [[00:04:41](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=281)]
GROUP_REDUCE is this late expansion to that, but there's no reason you shouldn't be able to have multiple reductions. I think getting rid of the REDUCE axis makes sense.

##### **Chenyu** [[00:04:52](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=292)]
I think back-to-back reductions are fine. But imagine you have a case that's parallel, and there are cases where you want to do different things for those parallel reductions. Then it's not clear what your axis is.

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=307)]
Do you mean parallel as in they share a RANGE?

##### **Chenyu** [[00:05:10](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=310)]
Yeah.

##### **Geohot** [[00:05:12](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=312)]
Sharing a RANGE is not something that's well supported. You can get into situations where it's unsolvable.

##### **Chenyu** [[00:05:23](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=323)]
Yeah, so I don't think we want to mess around with that area yet. I also removed another big part from x86. It's kind of annoying; we really want someone to own x86. What I did was try to remove as many incomplete things as possible while preserving tests that passed without big issues. For some of it, I just added a failing test because it touches the active RDNA3 backend, which I don't feel like changing now. Overall, it still looks pretty complicated for what it is.

##### **Geohot** [[00:06:27](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=387)]
I like the cleanup to the register allocator. Raine got that merged. But we really have to make INS into CALL. I don't know how much that's going to help, but there are a lot of intermediate places where, for RDNA3 and x86, we have full descriptions of the instructions in UOps.

##### **Chenyu** [[00:07:03](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=423)]
We can discuss those in the later items. One thing I want to add: I was looking into some of the late decompositions. We have things like `fast_idiv`, which tries to rewrite IDIV into MULs and shifts. I think those should eventually be similar to instruction selection and merge with it.

I was comparing what LLVM is currently doing with what RDNA3 is currently doing to decide whether I want to enable it again. It's disabled now because there seemed to be a bug before. I think it's fine now, but it's not really faster, so I'll just leave it there.

##### **Geohot** [[00:07:54](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=474)]
I think it should be CALL. You don't even have to use INS. This is what I mean by CALL and INS being the same thing. When we have a decomposition, this should also make rendering a lot faster. Our backends should basically be able to render CALLs.

##### **Chenyu** [[00:08:13](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=493)]
What does that even mean? If that's the case, what cannot be expressed by CALL? Every ALU is a CALL.

##### **Geohot** [[00:08:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=506)]
Think about the decomposition for SIN. You could imagine replacing SIN with a CALL. The CALL takes in the parameter and outputs the SIN, and that would render to a function, like a C function. Even assembly backends can support CALL. Everything can support CALL.

##### **Chenyu** [[00:08:58](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=538)]
My point is that the CALL here is just what's currently right before the decomposition or ALU. You still have this thing, and you still need to decide what it becomes. If we do this in the renderer, then the renderer becomes the part that does the selection.

##### **Geohot** [[00:09:18](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=558)]
The renderer definitely shouldn't do the selection, but it should support CALLs. This doesn't get you out of choosing whether to do the selection. Instruction selection should be a late pass, and it should look more like a CALL. That way, when we have ten SINs, it doesn't insert this huge UOp blob ten times; it just inserts a CALL to the same thing.

##### **Chenyu** [[00:09:41](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=581)]
Yeah, I think that makes sense.

##### **Geohot** [[00:09:43](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=583)]
I think the generated code will be faster too.

##### **Chenyu** [[00:09:47](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=587)]
Why would it be faster? Because it has a quick thing for the function?

##### **Geohot** [[00:09:52](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=592)]
Because of the I-cache. It depends on how big it is. You have an instruction cache that's going to be around 32 kilobytes. If your program starts to get large, then you're out of the instruction cache.

##### **Chenyu** [[00:10:10](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=610)]
Okay. Anyway, that's it. I was also testing GPT-6. I thought I'd have it fuzz some random stuff and fix the bugs that it finds. That would be nice.

##### **Geohot** [[00:10:29](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=629)]
I tried exactly this. I told it to find bugs and replace them with negative line diffs.

##### **Chenyu** [[00:10:37](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=637)]
That would never work. You need to be more precise than that.

##### **Geohot** [[00:10:44](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=644)]
Yes, you need to be more precise. It was very good at finding bugs in the fast USB transfer path. There were some subtle race conditions that it found. But every time I try to get it to do spec work, it's exactly the same. It's worse than Kimi. It's the same as the other GPTs: it just makes the test pass.

I think they're great at fuzzing and finding bugs. Anything where there's no way it can do wrong is incredible.

##### **Chenyu** [[00:11:18](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=678)]
Now it's very good because it will randomly write a lot of frontend code and try to test it.

##### **Geohot** [[00:11:27](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=687)]
I cleaned up a whole lot of bugs. I felt bad that B1tg kept fixing bugs in my AMD kernels, so I ran GPT a bunch of times. Hopefully the bugs are gone.

##### **Chenyu** [[00:11:43](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=703)]
We can decide who will fix the whole ASSIGN thing, but let's move on to rangeify and CALL.

##### **Geohot** [[00:11:53](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=713)]
I did no work on rangeify at all. I started working on CALLify instead. CALLify is a huge mess of code, and I feel bad for what I put in to remove RETURNED. RETURNED was bad, but the thing before RETURNED was even worse. Now, at least, I think I have the spec correct.

You can create unbound BUFFERs as inputs to CALL and as inputs to a local CALL, which is what you use to call a custom kernel. Those unbound BUFFERs don't get moved outside CALLify, so they don't become global BUFFERs. They stay as BUFFERs in the local CALL. You need that in order to optimize them. Otherwise, they can't be optimized, and you end up with too many buffers and too many stupid copies.

CALLify has all this logic to do transformations. When you put a CONTIGUOUS in the tensor graph, do you expect it to become a global BUFFER? I don't know. What do you expect?

##### **Chenyu** [[00:13:19](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=799)]
We changed the definition a while ago. In my mind, CONTIGUOUS does nothing. It promises that the output needs to be contiguous, but if I really want to build a buffer, then I have to call CLONE.

##### **Geohot** [[00:13:53](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=833)]
I think CLONE's behavior is clear. `.clone()` means assigned to a named BUFFER. If you do `b = a.clone()` and `c = a.clone()`, you're going to get different buffers for both of them. That's what's promised by the spec. Is that what you want?

##### **Chenyu** [[00:14:11](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=851)]
Yeah, I think that's why CLONE was introduced initially.

##### **Geohot** [[00:14:18](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=858)]
Those buffers can never be optimized. When we do COPY now, do you think its output should go into a global BUFFER?

##### **Chenyu** [[00:14:33](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=873)]
That's very similar to CONTIGUOUS. I imagine tinygrad can just remove it. It gives me a virtual blob that's promised to be on some device.

##### **Geohot** [[00:14:45](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=885)]
Currently, COPY behaves the same as COPY plus CLONE on DISK. If you don't do this, it ends up reloading from disk every time.

What I've been trying to work with the LLMs to do, to little effect, is enforce a spec where the only way you're ever going to get a BUFFER in the external tensor graph is with `.clone()`.

##### **Geohot** [[00:15:21](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=921)]
Or REALIZE.

##### **Chenyu** [[00:15:27](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=927)]
Not even REALIZE, because we can SHRINK and it doesn't create a new BUFFER.

##### **Geohot** [[00:15:35](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=935)]
That's another issue. Do you want REALIZE to be on the base, or do you want REALIZE to really be on the end thing? What we want is an API that's understandable to the user. All this bespoke logic where it sometimes injects a global BUFFER and sometimes doesn't isn't workable.

##### **Chenyu** [[00:16:08](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=968)]
Eventually, a lot of this fine-grained control comes from places where you want to manage memory better. Imagine that instead of letting a pattern do the work for you, you allocate a very big thing and try to finely control the memory for each tensor. That's very confusing and feels like premature optimization.

##### **Geohot** [[00:16:40](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1000)]
At least now we have good language to talk about it. We have the bound BUFFER, the unbound BUFFER, and the CALLify BUFFER, which are three different things.

##### **Chenyu** [[00:17:00](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1020)]
Describe each kind in one sentence.

##### **Geohot** [[00:17:03](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1023)]
An unbound BUFFER does not have real backing. It may be optimized out in rangeify, and it won't be inserted into the global tensor graph.

##### **Chenyu** [[00:17:16](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1036)]
Kind of a free variable.

##### **Geohot** [[00:17:20](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1040)]
Right. A bound BUFFER is bound to a physical location on the device and cannot be memory-planned. It will always be inserted as an input to CALLify.

What CONTIGUOUS does now is create a bound BUFFER, but I think we have to change it to do nothing in CALLify. If you want a BUFFER in the external graph, you have to use CLONE.

The problem I ran into is that you start inserting all these CLONEs everywhere and realize that gradients don't work. Gradients work well through CONTIGUOUS because it's just nothing. But what's the gradient of an AFTER? You can argue that the proper gradient of an AFTER is source one of the STORE, which is probably right for an AFTER-STORE-BUFFER construction. But then you get AFTERs that don't have STOREs. What if an AFTER is on another AFTER, or on multiple things? What's its gradient?

That's the problem I've been working on. I saw you say that, in theory, you thought the output of that thing should be zero. I don't know, but it definitely shouldn't be.

##### **Chenyu** [[00:19:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1166)]
I don't even know why it has a value now.

##### **Geohot** [[00:19:33](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1173)]
You would assume it behaves the same as just squaring twice.

##### **Chenyu** [[00:19:44](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1184)]
Yeah, so 32 is the derivative of x to the fourth at x equals two.

##### **Geohot** [[00:19:54](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1194)]
Wait, 32 isn't two to the fourth. Two to the fourth is 16.

##### **Chenyu** [[00:20:00](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1200)]
Yeah, but you take a derivative, so you get four times x cubed.

##### **Geohot** [[00:20:08](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1208)]
Okay, four x cubed. That makes sense. It definitely shouldn't be 64. But if you maintain that it should be zero and CLONE is a detach, then CLONE behaves very differently from CONTIGUOUS.

##### **Chenyu** [[00:20:33](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1233)]
What do other frameworks do with this?

##### **Geohot** [[00:20:39](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1239)]
In PyTorch, CLONE behaves like CONTIGUOUS. Then I started thinking through all these cases. What if I have two STOREs to the same BUFFER and there's no ordering between them? What's my gradient?

##### **Chenyu** [[00:21:09](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1269)]
I think we always, or at least for ASSIGN, try to keep an order, at least code-flow order.

##### **Geohot** [[00:21:23](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1283)]
We might have some stuff that tries to do that, but I don't think it's correct. I put an extra AFTER in all of them. I think what I'm going to do is tighten up the gradient spec to work only on simple cases. Right now I can just make that second ASSIGN not work and say sorry.

I can tighten up that spec. Then we have all these write-after-read and read-after-write hazards. There's a big chunk in CALLify that supposedly handles them, but it's wrong.

##### **Chenyu** [[00:22:01](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1321)]
I added ten or twenty tests that I believe cover all of the cases.

##### **Geohot** [[00:22:08](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1328)]
No, it's still wrong. If you ask GPT, it can come up with things that are obviously wrong. I'm working on this before rangeify. I don't know if I'll be able to do it this week, but that's what happened to rangeify: it turned into CALLify work.

I got FlashAttention merged, which is kind of fun. I've also been playing around with a GPU operating system. This is eventually where we want to go: hijack the whole GPU and manage our own kernel launches. Instead of launching kernels, with some small amount of effort tinygrad can compile everything straight into a megakernel. Whether that's faster or not, we'll see, but we should at least have the option.

##### **Chenyu** [[00:23:30](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1410)]
Are we getting more Turing-complete stuff?

##### **Geohot** [[00:23:36](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1416)]
Nothing should have to be Turing-complete. I guess you have one outer loop that you can argue is a Turing-complete loop, but Turing completeness only gets really bad when you have data-dependent behavior.

##### **Chenyu** [[00:23:56](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1436)]
If everything is static, you just need to promise that it keeps progressing.

##### **Geohot** [[00:24:05](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1445)]
It's just this forever loop. You can figure out whether it halts or not: it clearly doesn't halt. But that's fine. It's not like you have to do high-level analysis on this. The operating system is written in tinygrad, but in low-level UOps.

##### **Chenyu** [[00:24:33](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1473)]
Let's move on. Next is CI.

##### **Chrism** [[00:24:37](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1477)]
The big change is that we no longer have comma 3Xs in CI at all. It's all comma fours with Chestnuts. That's nice; it simplifies the architecture a little.

I got GARM, the GitHub Actions Runner Manager, up and running. It's running on Gateway 2 right now. It isn't exposed to the internet, but it eventually has to be so we can receive GitHub webhooks. You can look at it. It needs a password, which is in infra. There's a file in the secrets folder that says how to do that.

##### **Geohot** [[00:25:25](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1525)]
When you say it has to be exposed to the web, you should be able to do that through the Cloudflare Gateway.

##### **Chrism** [[00:25:29](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1529)]
Yes, that should work. I have a base image building itself. Gitea can use the GARM runners now, and there's a pool set up for it.

Unfortunately, you can't share pools. We'll have one pool for Gitea and one for GitHub, and you can't share runners between them.

##### **Geohot** [[00:25:59](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1559)]
Why not?

##### **Chrism** [[00:26:02](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1562)]
It doesn't let you share pools like that. You need one pool for the Gitea org and another for the GitHub org.

##### **Geohot** [[00:26:12](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1572)]
Both of them have to be able to use the entire computer.

##### **Chrism** [[00:26:18](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1578)]
The runners can use all the compute allocated to them, but the pools the runners are drawn from need to be separate.

##### **Geohot** [[00:26:31](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1591)]
That doesn't work. We can't have half the computer reserved for GitHub and half reserved for Gitea. We can't have anything reserved like that.

##### **Chrism** [[00:26:53](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1613)]
The other question is whether we're still going to use Gitea for anything. I was using it for testing earlier.

##### **Geohot** [[00:27:02](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1622)]
Definitely. I really do want to work on both.

##### **Chrism** [[00:27:08](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1628)]
This may require some architectural changes to GARM. I'll look. This also needs to be under the tinygrad account, in the tinygrad org on Gitea.

##### **Geohot** [[00:27:47](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1667)]
That's fine.

##### **Chrism** [[00:27:53](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1673)]
I'll think about how to do that. Given the way GARM registers these webhooks, it may require a significant amount of engineering work.

##### **Geohot** [[00:28:09](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1689)]
I don't understand that. The pools are dynamic.

##### **Chrism** [[00:28:14](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1694)]
That's true. It should be possible. The issue is that you also have to install different runners. If you have warm workers waiting for jobs, each has to run either the Gitea runner or the GitHub runner. It can't run both.

##### **Geohot** [[00:28:41](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1721)]
I'm asking Chat about this now. It says you can't share a pool, but both pools can use the same physical compute capacity. So I think you want two pools with a constraint saying M plus N must be less than the total.

##### **Chrism** [[00:28:58](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1738)]
I didn't see that in the docs, but that seems possible.

##### **Geohot** [[00:29:07](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1747)]
That also sounds like the kind of thing that's easy to add if we have to. Two pools are totally fine. I don't think we should try to make them share a pool; the pools can expand and contract dynamically.

##### **Chrism** [[00:29:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1766)]
This is definitely possible through an API. The question is whether you can do it natively, or through some system that enforces a maximum number of runners across both pools. Right now, you configure the maximum number of runners separately in each GARM pool.

##### **Geohot** [[00:29:56](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1796)]
Maybe Incus can do this. Maybe Incus can tell GARM that there are no VM resources available.

##### **Chrism** [[00:30:05](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1805)]
That's kind of what we want anyway. It would be nice to enforce the limits there too.

##### **Geohot** [[00:30:13](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1813)]
Incus supports it.

##### **Chrism** [[00:30:15](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1815)]
Great. It would also be nice for people to SSH into these machines, use them directly, and tell the Actions runner not to schedule anything on them. The scheduler runs on the gateway while Incus runs on the machine doing the work. It would be annoying if, every time you wanted to use a GPU, you had to log into the gateway, run a command, log out, and then log into the machine you wanted. It would be much nicer to SSH into the real machine and say, "I'm claiming this GPU for now."

##### **Geohot** [[00:30:59](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1859)]
Take it out of the pool, sure. Check what I posted. You can share an Incus project and limit the pools there.

##### **Chrism** [[00:31:14](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1874)]
That makes sense.

##### **Geohot** [[00:31:17](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1877)]
It says that it doesn't provide fair queuing, but I'll pretend not to have read that.

##### **Chrism** [[00:31:22](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1882)]
I don't think there will be that much contention. In any case, that's set up. I'm going to try to get CI running on Gitea for tinygrad now. I'm particularly excited to get this working for benchmarks because I'm hopeful a lot of the flakiness goes away.

Nimlgen just posted in CI Failures that when you cancel a job running an MLPerf workload on AMD, for some reason it can't kill the leftover PIDs. I've seen that happen a lot. It's frustrating. This is why you have to use VMs: if you shut down the VM, it just goes away.

I'm trying to think if there's anything else important for CI. We'll have to figure out what to do for the Macs. GARM doesn't have runners for macOS. It may not be too hard to make our own; the GARM dispatcher is pretty simple. But there's also the question of whether we want to manage the Macs in GARM in the first place.

##### **Geohot** [[00:32:55](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1975)]
I think we can manage them in GARM. They'll probably still be VMs, but they might be long-running VMs.

##### **Chrism** [[00:33:08](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1988)]
If they're long-running VMs, maybe they don't go in GARM, because it's designed for ephemeral VMs.

##### **Geohot** [[00:33:17](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=1997)]
Then we can manage them separately. It would be nice to put them in GARM, but let's get everything else migrated first. We can leave the Macs for now.

##### **Chrism** [[00:33:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2006)]
I'll see whether we can make them ephemeral, which would be nice and simple. If not, we'll figure it out. It is nice to log into GARM and see all the usage there.

The other thing I wanted to mention is SSH access to the VMs. To set it up, it looked like I had to do a lot of SSL work: make our own certificates and ensure they're installed properly everywhere. Did you run it?

##### **Geohot** [[00:34:05](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2045)]
Yeah, I did it. It was fine. What it asks is that if you want to use the WebSocket shell, you can't enable it over HTTP. You have to use HTTPS, but that's fine. I still want our VMs to have our own certificate installed anyway, so we can use a proxy. I think that's the solution to the internet caching problem.

##### **Chrism** [[00:34:47](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2087)]
I thought about that too. We'll probably run a MITM proxy or Squid proxy. Incus already runs dnsmasq for all the VMs. For whatever services or URLs we decide to cache, such as GitHub user content, we can rewrite the DNS query to our caching proxy.

##### **Geohot** [[00:35:24](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2124)]
That's probably even nicer than trying to support some proxy-chain setup.

##### **Chrism** [[00:35:32](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2132)]
I think that's the simplest way. Routing all traffic through the proxy and telling it to cache only certain things would create a lot of traffic we don't need.

##### **Geohot** [[00:35:44](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2144)]
I think just a few DNS rewrites are probably good.

##### **Chrism** [[00:35:49](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2149)]
That's most of the CI stuff. It's all in infra. I put as much as I could there. There are certain things you have to configure in the web UI, so I'll document those and put as much configuration as possible into infra.

##### **Geohot** [[00:36:06](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2166)]
Just make sure it's documented.

##### **Chrism** [[00:36:09](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2169)]
Yes. The other thing is that NOLOCALS is gone now. Hopefully that already made things easier for Nimlgen, or continues to make things easier for him.

##### **Geohot** [[00:36:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2186)]
Cool. Next is LLaMA. Hello? Qazalin?

##### **Geohot** [[00:37:04](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2224)]
Let's move on first. GPT-OSS.

##### **Wozeparrot** [[00:37:10](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2230)]
I posted a new run, the fastest one yet. It's at two hours and 36 minutes, 700 milliseconds a step.

##### **Geohot** [[00:37:30](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2250)]
Cool. What was fixed to get there, and what do we have left?

##### **Wozeparrot** [[00:37:33](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2253)]
This is just GEMM optimization, taking our existing kernels and optimizing them more. We're currently under 600 milliseconds of compute time.

##### **Geohot** [[00:37:47](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2267)]
Great. So it's just comms?

##### **Wozeparrot** [[00:37:54](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2274)]
Yeah, it's just comms right now. If we fix comms, this goes under 600 milliseconds a step.

##### **Geohot** [[00:38:06](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2286)]
If we're at 600 milliseconds, what's the total time?

##### **Wozeparrot** [[00:38:12](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2292)]
We want to be slightly under 600. At 600, we should be at two hours and three minutes.

##### **Geohot** [[00:38:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2306)]
Assuming there's no startup time. How much is startup time now?

##### **Wozeparrot** [[00:38:31](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2311)]
Several minutes. We're spending about nine minutes on startup now, actually a little more, almost ten minutes.

##### **Geohot** [[00:38:52](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2332)]
That's good, because we know how to fix that if we really have to. There's no reason we can't do that offline. But we should still get to 600 milliseconds a step. How much is left that isn't communication?

##### **Wozeparrot** [[00:39:19](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2359)]
The attention is still pretty slow. I've been looking into potentially moving to MXFP4 attention. The B200 submissions all use MXFP4 attention, and that's currently our slowest kernel.

##### **Geohot** [[00:39:38](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2378)]
How much time would we save if we did that?

##### **Wozeparrot** [[00:39:41](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2381)]
Probably another 20 milliseconds.

##### **Geohot** [[00:39:44](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2384)]
That's a decent amount. But it seems like the thing we really need to focus on is comms.

Oh, by the way, I registered MLPerf, so you should get an email. Let me know if there's anything wrong. It's a TinyRed email.

##### **Wozeparrot** [[00:40:22](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2422)]
I haven't gotten anything yet.

##### **Chenyu** [[00:40:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2426)]
I think this is just for registration.

##### **Wozeparrot** [[00:40:30](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2430)]
Maybe they send things later when they open submissions.

##### **Geohot** [[00:40:45](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2445)]
Are you confident we can get comms done this sprint?

##### **Wozeparrot** [[00:40:53](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2453)]
Yeah, I'll look into comms this sprint.

##### **Geohot** [[00:41:00](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2460)]
Are you pretty confident we can do it, or has someone already looked into comms? Maybe Qazalin is here and can tell us. She's typing.

##### **Qazalin** [[00:41:20](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2480)]
Hi, sorry. I kind of slept, honestly.

##### **Geohot** [[00:41:22](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2482)]
Hi. You're good. I know how annoying the time is for this meeting in Hong Kong.

##### **Qazalin** [[00:41:33](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2493)]
Sorry about that. I'm awake now. What was the discussion?

##### **Geohot** [[00:41:41](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2501)]
Any improvements on LLaMA speed? We'll start there.

##### **Qazalin** [[00:41:47](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2507)]
One hour and 53 minutes is our latest time. I just trained today.

##### **Geohot** [[00:41:58](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2518)]
How much better is that than what we had?

##### **Qazalin** [[00:42:00](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2520)]
One hour and 55 minutes was last week. I honestly think it's all about making the GEMM faster.

##### **Geohot** [[00:42:16](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2536)]
Is this the same GEMM that GPT-OSS is using?

##### **Qazalin** [[00:42:21](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2541)]
No, that's different. It's a different FP4 GEMM. This is the difference between NVIDIA and AMD on the same shapes.

##### **Geohot** [[00:42:37](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2557)]
NVIDIA's is kind of crappy too.

##### **Qazalin** [[00:42:39](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2559)]
This is MXFP4. Their MXFP4 GEMMs that they actually submitted are over 60% MFU. This is apples-to-apples MXFP4. They have an MXFP4 kernel, and I'm going through it with Chat to figure out what we can do.

##### **Geohot** [[00:43:06](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2586)]
How complete is the VIZ stuff now?

##### **Qazalin** [[00:43:09](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2589)]
The VIZ stuff is much better now. There's a screenshot of the new VIZ in the channel.

##### **Geohot** [[00:43:21](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2601)]
I see. Good. I'm happy we're now getting all the SIMDs, and there actually is only one wave. That would make sense.

##### **Qazalin** [[00:43:28](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2608)]
One wave per SIMD. It doesn't actually wave-specialize; it just takes over the whole SIMD.

##### **Geohot** [[00:43:42](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2622)]
That makes sense. The conversation was that GPT-OSS has communication issues. It's wasting 100 milliseconds on communication. How has progress been on LLaMA communication, and is there a reason GPT-OSS communication is harder?

##### **Qazalin** [[00:44:06](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2646)]
From what I saw in the Discord channels, it's exposed communication, like SEMA. S-E-M-A.

##### **Geohot** [[00:44:25](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2665)]
Can you post a `VIZ=1` so we can see the non-overlapped communication?

##### **Wozeparrot** [[00:44:33](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2673)]
Yeah. I have to run that, so it will be a while.

##### **Geohot** [[00:44:42](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2682)]
Just post it at some point. We need to figure out whether we want to move to communication on the CUs or whether it's just scheduling issues with SDMA. For LLaMA, did you end up moving it or not?

##### **Qazalin** [[00:45:00](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2700)]
For the topo-sort issues, some can be fixed with topo-sort. Others are really just a kernel problem.

##### **Geohot** [[00:45:17](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2717)]
We're at 1:53. What's left? Is it only GEMMs, or is there more?

##### **Qazalin** [[00:45:27](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2727)]
It's only GEMMs. Even if I fix the communication stalls, they're really small and won't give us the speed we need. NVIDIA does it in one hour and 22 minutes.

##### **Geohot** [[00:45:42](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2742)]
That's still a big difference. We need to get there. We have to get another three or four minutes before MLPerf.

We could write something to cache it: pickle the UOps of the whole schedule and get the JIT to cache to disk. But that's a last thing to do. Let's not do that. If there's nothing to gain on comms and it's mostly GEMM work, how much of this work can also apply to GPT-OSS? I know it's not the same GEMM.

##### **Qazalin** [[00:47:14](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2834)]
I'm hoping that `VIZ=2` being more comprehensible and usable on CDNA will help. I think they use HipKittens, or at least you can use HipKittens. I don't know whether the assembly work will help much.

##### **Geohot** [[00:47:37](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2857)]
What's our current GPT-OSS GEMM?

##### **Wozeparrot** [[00:47:42](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2862)]
It's a custom HipKittens MoE GEMM.

##### **Geohot** [[00:47:53](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2873)]
It sounds like we just have to fix communication. It's all overlapped correctly with LLaMA. Is there any reason LLaMA is easier than GPT-OSS? I guess it's smaller.

GPT-OSS uses ZeRO-2, so the optimizer is sharded. We're just not overlapping things correctly.

We're going to get more MFU on the GEMMs, and hopefully this work can apply to the HipKittens ones too.

##### **Qazalin** [[00:48:52](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2932)]
We should look at these HipKittens kernels with VIZ.

##### **Geohot** [[00:48:57](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2937)]
Maybe you want to look at the GPT-OSS kernels once you have `VIZ=2` working and see if you can make them faster. We can work on this together. There's a communication half and a GEMM half. We should be able to hit both our targets.

When's your talk?

##### **Qazalin** [[00:49:29](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2969)]
The talk is Saturday, September 19.

##### **Geohot** [[00:49:35](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2975)]
Cool. Thanks. Let's move on. Next is HCQ2.

##### **Nimlgen** [[00:49:52](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=2992)]
HCQ2 is the default now. HCQ1 is gone. On AMD, you can still use `HCQ2=0`. I still need to add all-to-all communication to HCQ2, but everything seems faster with HCQ2 after the rewrite, with a single compiled program.

This week I'll focus on the DigitalOcean work, meaning the GPU virtual functions.

##### **Geohot** [[00:50:39](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3039)]
How annoying is that? How much time will it take?

##### **Nimlgen** [[00:50:45](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3045)]
I don't know. I haven't looked yet; this week was only HCQ2. I'll take a look.

##### **Geohot** [[00:50:53](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3053)]
If you think it will be more than a week of work, maybe we just don't do it, especially if it's bespoke work for that. But if it reveals fundamental bugs, then it's worth it.

I'm looking at HCQ2 in VIZ now. How come I don't see the generated C code? It should be right there. Why am I on a CL device? `No module named extra.hcq_ops_amd_old`. Okay, now it worked. So CL doesn't generate C code?

##### **Nimlgen** [[00:52:06](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3126)]
I have the Metal backend. I just need to clean it up. This week I'll focus on the other backends. I'll remove all the classes we still have in HCQ2 and merge them with Device, Allocator, and Buffer.

##### **Geohot** [[00:52:29](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3149)]
Amazing. These functions look great now. These HCQ submit functions look great.

##### **Nimlgen** [[00:52:42](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3162)]
I also tried to implement CALLs, rendering several CALLs inside one C file so we can save some UOps on USB.

##### **Geohot** [[00:53:10](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3190)]
I think we want that. We also talked about it for the decompositions. That's a general direction we're going anyway. If you don't need it right now, I would probably wait until someone else does it.

##### **Nimlgen** [[00:53:26](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3206)]
It's probably working fine without that in terms of speed. It's already much faster than what we had last week. But I'm not sure how the UOp graph should look. In my current implementation, inside one SINK we have a CALL and another SINK.

##### **Geohot** [[00:54:03](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3243)]
I see CALLs inside a SINK. I don't totally understand it. Can you post a screenshot?

##### **Nimlgen** [[00:54:21](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3261)]
I think I posted one in HCQ, but it will take a little time to post a new one.

##### **Geohot** [[00:54:39](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3279)]
That looks right. What do you think the problem with it is?

##### **Nimlgen** [[00:54:45](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3285)]
No problem, I think.

##### **Geohot** [[00:54:48](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3288)]
Then we just have to do it. Whether you really need that SINK, or whether the SINK should become the CALL, is a question. No, the SINK can't become the CALL. It should stay a SINK with the name and everything. That makes sense. It gets rendered once up top, and then CALL can call it by name.

After getting the remaining HCQ stuff cleaned up, I think your highest priority is getting two machines training LLaMA.

##### **Nimlgen** [[00:55:33](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3333)]
I also plan to do that this sprint. I think we have good abstractions after USB. USB was the hardest one.

##### **Geohot** [[00:55:46](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3346)]
Did those cables come in yet, Chris?

##### **Chrism** [[00:55:50](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3350)]
Yes, the cables are here. I need to swap the cards around and install them whenever that's needed.

##### **Geohot** [[00:56:00](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3360)]
We'll make sure you have good hardware. I don't know how much you've looked at the topology of the MI350 machines. Each GPU has a three-port PCIe switch. One port is the host, one is the GPU, and the other is the Broadcom network card. Each GPU has its own dedicated Broadcom network card that connects to another GPU. That gives you an idea of the topology.

Should we be good with HCQ2 to submit the function to both machines?

##### **Nimlgen** [[00:57:30](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3450)]
I'll think about that, but currently there's no REMOTE for HCQ2.

##### **Geohot** [[00:57:40](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3460)]
You're welcome to kick everybody else off R5 and R6 and get those two training as a little cluster. We should have tons of bandwidth between the two machines.

To recap our energy contract, one payout is for LLaMA on two machines. One payout is for GPT-OSS below a certain speed. The third payout is for GPT-OSS on two machines below an even more aggressive speed. It's okay if we miss the last one, but I definitely want to get LLaMA training on both machines as soon as we can.

Great work getting HCQ2 merged as the default. I know it was a bit of a struggle, but hopefully it's a lot simpler now.

##### **Chenyu** [[00:59:06](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3546)]
Let's quickly go through the rest of the items. Any issues for comma?

##### **Chrism** [[00:59:13](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3553)]
I don't think so. They're definitely interested in speed. They always come back saying they want it to be a little faster.

I don't know if you saw, but there's a new ONNX custom op in the tinygrad domain called CONTIGUOUS, which allows them to inject contiguous operations. They're looking for additional control to express this sort of thing and get a little more speed. I think that ONNX op makes sense for them.

##### **Chenyu** [[01:00:15](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3615)]
Is Raine here? Any comments on RDNA3?

##### **Geohot** [[01:00:22](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3622)]
I think we're getting close. We got our first x86 thing merged. A few more cleanup PRs and I think it's getting pretty close.

##### **Chenyu** [[01:00:43](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3643)]
Anything else?

##### **Geohot** [[01:00:45](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3645)]
The GPU Ocelot bounty. Someone seems to have it working. It doesn't look too much like AI crap.

##### **Chrism** [[01:01:14](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3674)]
The problem is that I don't know enough about Ocelot to know whether the changes they made are reasonable. They probably are. It's probably fine.

##### **Geohot** [[01:01:32](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3692)]
That's why I asked whether they did it just to target the tests. As far as the bounty goes, I don't think we're going to get a better submission than this. It doesn't look obviously AI-generated, and it passes the tests.

##### **Chenyu** [[01:01:55](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3715)]
If it passes the tests and seems like we can maintain it, it's probably fine. It's very hard to get this right. I found a bunch of bugs in our AMD emulator too. It's hard to get everything correct, and we don't necessarily have full test coverage for all possible generated code.

##### **Chrism** [[01:02:22](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3742)]
It's definitely true that we'd prefer it in Python, in the repo, and in UOps rather than in Ocelot. That's still better than some complicated C++ thing that no one ever reads.

##### **Geohot** [[01:02:35](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3755)]
That sounds good in theory, but I think we should basically merge this. It's not clear to me that this person's PRs are significantly worse than Ocelot itself.

##### **Chrism** [[01:03:01](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3781)]
That's true. We'll see what they say about rebasing it.

##### **Geohot** [[01:03:13](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3793)]
I think we should take the fork into `tinygrad/gpuocelot`.

##### **Chrism** [[01:03:21](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3801)]
They already have a PR against `tinygrad/gpuocelot`.

##### **Geohot** [[01:03:29](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3809)]
Cool. Do we have CI on that?

##### **Chrism** [[01:03:32](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3812)]
It builds and runs the Ocelot test suite.

##### **Geohot** [[01:03:53](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3833)]
I'll get this merged into our Ocelot. After I merge it, do you want to update the CI?

##### **Chrism** [[01:04:01](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3841)]
Yeah, I can do that.

##### **Geohot** [[01:04:03](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3843)]
Cool. Sounds good. Anything else? No? Okay.

##### **Chenyu** [[01:04:23](https://www.youtube.com/watch?v=ZvzpGOMjeF4&t=3863)]
We'll probably discuss whether we need to change the meeting time for next week. We'll discuss that later. That's it for this one. Thank you, everyone. See you next week. Bye-bye.
