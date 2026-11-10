# 2026-11-10 Meeting

### Meeting Agenda

**Time:** new meeting #45, 11/10 12pm Hong Kong time
- company update
- AFTER, MULTI, explicit LOAD
- assembly
- NVMe, SDMA
- course, UIR
- MLPerf, LLM serving
- machines and tiny DC
- bounties, Comma


### Audio

[Youtube Link](https://www.youtube.com/watch?v=Bksf3EdW_Zs)

### Highlights

- **[Company Update](#geohot-000005)**: $1.5M in sales this week from 25 boxes sold. Geohot thinks they were priced too cheaply, and the next batch will cost more.
- **[MI300 Machines](#geohot-000030)**: Batch one sold out quickly, and the cash goes toward parts for more machines. Most of the GPU cost has been recovered. Binning software is being built, and only about a third of the GPUs work.
- **[NVIDIA Returns to the Shop](#geohot-000136)**: PNY wanted KYC on every NVIDIA GPU customer, and Geohot refused. PNY will instead sell if tinygrad only sells to U.S. customers, so NVIDIA should come back in stock.
- **[Explicit vs. Implicit LOAD](#geohot-000436)**: Geohot compares LOAD to broadcasting. It is only needed when an ALU op like ADD touches GLOBAL address space, not for a reshape. Week six adds a preprocessor that inserts implicit loads, resolves broadcasting and handles dtype promotion.
- **[MULTI After Rangeify](#geohot-000934)**: MULTI has to happen after rangeify, with STAGE replacing UNSHARD. The only difference between the two is that UNSHARD lets you specify where the axis is inserted.
- **[x86 Moves to CALLs](#qazalin-001301)**: CUSTOM and CUSTOMI are removed, and everything is now a CALL. A new ASM UOp holds LOADs and STOREs describing what is read and written. The x86 backend is being ported this week, with RDNA3 next.
- **[NVMe and SDMA](#nimlgen-001616)**: NVMe work is merged in master and reached about 223 GB/s on tiny-s3. SDMA improvements are being brought over from both fast LLM branches to reduce latency.
- **[Course and STACK](#geohot-002209)**: Studentgrad is 853 lines at the end of week five, and LLMs can no longer find failing UIR tests. STACK is now charged like an ALU op so it can't be exploited. Codex flagged Geohot for cybersecurity because the bug hunting went so deep.
- **[Frontend, Compiler, Runtime](#geohot-002417)**: Geohot wants tinygrad split into three explicit phases. The frontend converts everything to UIR, the compiler transforms UIR into UIR down to binaries, and the runtime stays as simple as possible. CALLify is also being simplified.
- **[MLPerf Results](#wozeparrot-002955)**: Final results are locked, and Wozeparrot attends a press briefing on Wednesday. Results come out at the end of the week.
- **[Moving LLM Serving Off Cloudflare](#geohot-003332)**: Cloudflare's 120-second timeout hurts long prefills, so llm.tinygrad.win will move to tinygrad's own IP. The API-key check should sit very early in the reject path.
- **[Serving Capacity and GitHub API Keys](#geohot-003643)**: Each machine gets about 2,000 tok/s decode, with a goal of 3,000. At about 100 tok/s per user that is 32 users, and two machines could support about 100 people. Users would log in with GitHub for an API key worth about a million tokens, with router-side accounting.
- **[Data Center Decision](#geohot-004712)**: Geohot rejects major downtime and rearranging the room. He approves upgrading fans, opening more apertures to the outside, and tidying fire hazards like frayed cables and the Dell switch mounting. The target is about 10x airflow.
- **[Qwen 4 Hosting](#geohot-010312)**: Qwen 4 is expected this week, and Geohot wants tinygrad ready as one of the first hosts. Free tokens would go to anyone who signs up with GitHub.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=0)]
Let's get started. Let's start with company updates.

##### **Geohot** [[00:00:05](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=5)]
We made $1.5 million this week. We sold 25 of the boxes. I think we priced them too cheaply. I don't know, it's okay to price something cheap. The next batch will definitely not be that cheap.

##### **Geohot** [[00:00:30](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=30)]
Batch one of the MI300 machines sold out super fast, so we're working on getting them built. Get some money in so we can buy parts for a lot of machines. We made back not all the money we spent on the GPUs, but most of it. We're building software to bin the GPUs now. About a third of them work.

##### **Chenyu** [[00:00:56](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=56)]
Great.

##### **Chenyu** [[00:01:04](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=64)]
Any ETA on the shipping?

##### **Geohot** [[00:01:07](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=67)]
What?

##### **Chenyu** [[00:01:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=69)]
Any ETA for the machines?

##### **Geohot** [[00:01:13](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=73)]
Hopefully January, but we said Q1, so it might be later. The biggest lead-time item is those boards take a really long time to make. They have tons and tons of layers. All the other orders are going out pretty soon.

##### **Geohot** [[00:01:36](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=96)]
We can add NVIDIA back to the shop. PNY wanted us to basically KYC every customer we sell NVIDIA GPUs to. I'm like, "Bro, this just isn't worth it. I'm not participating in the fascist GPU control."

##### **Geohot** [[00:01:58](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=118)]
We sent them an email saying that, and they basically said, "We'll sell you GPUs, but you have to sign this thing saying you're only going to sell them to U.S. customers." That's fine. NVIDIA will probably come back in stock.

##### **Chenyu** [[00:02:18](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=138)]
Sounds good. Anything else for company updates?

##### **Geohot** [[00:02:25](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=145)]
I think that's it. We're making money, though. Big revenue this year.

##### **Chenyu** [[00:02:32](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=152)]
Big revenue, yeah. Technically, you can only account for those once the goods are delivered.

##### **Geohot** [[00:02:40](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=160)]
Once the goods are sold, sure. We've outlaid the cash for the goods.

##### **Chenyu** [[00:02:49](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=169)]
Liability for now.

##### **Geohot** [[00:02:52](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=172)]
Sure.

##### **Chenyu** [[00:02:55](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=175)]
We'll start with my item. I made a bunch of changes to AFTER. One of the main gaps between tinygrad and studentgrad's spec is that studentgrad explicitly adds a LOAD if you want a value out of that INDEX.

##### **Geohot** [[00:03:25](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=205)]
You have to use the LOAD to transform the address space from GLOBAL to ALU.

##### **Chenyu** [[00:03:33](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=213)]
I understand, but I'm not convinced yet that's a must.

##### **Geohot** [[00:03:42](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=222)]
You can do it like broadcasting, right?

##### **Chenyu** [[00:03:47](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=227)]
I mean inferring if you want such a LOAD or not.

##### **Geohot** [[00:03:54](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=234)]
I imagine that LOAD existing on the object, kind of like what we do in MULTI. In MULTI, we'll leave around the UNSHARD on the object stored in the Tensor. You could leave around the LOAD stored in the Tensor, and only remove it if you're trying to do assigns.

##### **Chenyu** [[00:04:19](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=259)]
When you write the IR, do you need to write that LOAD out or not?

##### **Geohot** [[00:04:26](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=266)]
In week six, you won't have to. Week six is where I'm adding all the syntax.

##### **Chenyu** [[00:04:33](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=273)]
So you plan to remove that?

##### **Geohot** [[00:04:36](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=276)]
You can view it as a form of broadcasting. You only need the explicit LOAD if you're doing an operation that's not allowed on address space GLOBAL. To do a reshape, you don't need a LOAD, but for an ADD, you have to do a LOAD. Just like broadcasting, I can detect if you're doing an ALU-only operation on a GLOBAL, and that's where you insert the LOAD.

##### **Chenyu** [[00:05:06](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=306)]
I see.

##### **Geohot** [[00:05:12](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=312)]
In week six, I'm going to separate studentgrad things into the preprocessor and the operation. The preprocessor resolves broadcasting, dtype promotion, and implicit loads.

##### **Chenyu** [[00:05:32](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=332)]
I have a giant thing showing that our current LOAD handling, add-load and remove-load, is suboptimal sometimes. It's never wrong, but it's bad. You can make a guess wrong or something like that.

##### **Geohot** [[00:05:54](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=354)]
Is there something for me to look at? Where is this?

##### **Chenyu** [[00:05:57](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=357)]
I have a big change on tinygrad that forces everything to be an explicit LOAD. I checked process replay, and several of the devectorizer results got much better code, or what looks like much better code. Some of the add-load things we're currently doing are probably not very efficient.

##### **Geohot** [[00:06:22](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=382)]
Interesting. I think add-load is done way too late. It should be done earlier. You're not allowed to put a GLOBAL into an ADD.

##### **Chenyu** [[00:06:41](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=401)]
I don't have a solution yet. I started this today because I was checking studentgrad. Some of the assign things in tinygrad probably need a better spec, just for the ordering stuff. When is it okay to determine the state of the LOAD? Technically, LOAD on the INDEX is not a statement. You can infer that, but we need code to infer it.

##### **Geohot** [[00:07:11](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=431)]
In studentgrad, I replace all LOADs with STAGEs, and I promise you the Tensor actually is that value at that time.

##### **Chenyu** [[00:07:21](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=441)]
That's your access model.

##### **Geohot** [[00:07:26](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=446)]
It's very explicit and easy to teach. I'm not 100% sure that's what we want in tinygrad.

##### **Chenyu** [[00:07:34](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=454)]
One issue with this ambiguity is that the only remaining gap where tinygrad doesn't pass studentgrad tests is some of our INDEX optimizations fold the INDEX out. When that INDEX can carry a side effect, it shouldn't be folded out. It's annoying to say sometimes it's a loaded value, and sometimes it should act on the INDEX.

##### **Geohot** [[00:08:10](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=490)]
Do you mean effects, like AFTER effects?

##### **Chenyu** [[00:08:14](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=494)]
No. When you have an INDEX, say INDEX less than three, it's not clear whether we mean in the index space, that range should only take the shrink less than three, or the value after loading is less than three.

##### **Geohot** [[00:08:38](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=518)]
I'm not following this. You mean bounds?

##### **Chenyu** [[00:08:42](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=522)]
I can paste examples somewhere. Tinygrad currently handles it very weirdly.

##### **Geohot** [[00:08:55](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=535)]
There's two compilers in the studentgrad repo now: rewrite and source. I'll delete the one in source, switch to just rewrite, and add the implicit-load stuff tomorrow.

##### **Chenyu** [[00:09:08](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=548)]
Sounds good. I also tried the MULTI thing we discussed in Hong Kong. MULTI gets a little simpler, but I still don't quite see how the interchange can happen.

##### **Geohot** [[00:09:25](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=565)]
What interchange?

##### **Chenyu** [[00:09:29](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=569)]
Doing MULTI after rangeify.

##### **Geohot** [[00:09:34](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=574)]
We have to do MULTI after rangeify. It's just going to be a STAGE instead of UNSHARD. UNSHARD and STAGE are very similar. The only difference is UNSHARD allows you to specify where the axis is inserted.

##### **Chenyu** [[00:09:56](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=596)]
Okay. MULTI looks a little simpler. Some of the numerical things to match or learn from... I think the only thing I want to do is the minus-zero default. It's annoying for IMAGE, because IMAGE out-of-bounds gives you positive zero, not negative zero.

##### **Chenyu** [[00:10:32](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=632)]
It doesn't really work with the PAD model. There are a few things we definitely want to fix. The copysign of minus zero should give negative numbers, not positive numbers. If you sum a bunch of negative zeros, in tinygrad the result depends on how many numbers you sum and the optimization. I think these are really bad, so I'm mostly focusing on fixing these.

##### **Geohot** [[00:11:04](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=664)]
Negative zero and positive zero are explicitly ignored by fast math. For all tinygrad stuff, in practice, we want fast math enabled. My theory about why compilers have a mode to disable it is that it's really hard to test. What's the spec you're testing?

##### **Geohot** [[00:11:33](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=693)]
The reason I made studentgrad so explicit is it becomes impossible to say how to test. "I'll just give all the floats some tolerance." Okay, what tolerance? There's no answer.

##### **Chenyu** [[00:11:56](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=716)]
There are simple properties for numbers. If you add a bunch of negative numbers, it probably should stay negative.

##### **Geohot** [[00:12:06](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=726)]
I don't even think fast math promises that. I read the Clang thing about fast math, and it explicitly said negative float zero and positive float zero are treated identically, or interchangeably. It comes down to how cheap these properties are to enforce. If they're free, sure, we like them. But if they require runtime branching...

##### **Chenyu** [[00:12:38](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=758)]
That makes sense. That's pretty much my stuff. We can move on to assembly.

##### **Geohot** [[00:12:57](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=777)]
Cannot hear you.

##### **Qazalin** [[00:12:59](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=779)]
Can you hear me now?

##### **Geohot** [[00:13:00](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=780)]
Yes.

##### **Qazalin** [[00:13:01](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=781)]
I came closer. I removed CUSTOM and CUSTOMI. It's now all just CALLs. This week I'm going to work on moving x86 to all CALLs. I have a draft PR open. I handwrite everything at this point, so I'm going by hand through the x86 backend.

##### **Qazalin** [[00:13:23](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=803)]
This is the state of the viz. It's a bunch of CALLs, and inside the CALL there's an ASM UOp. That purple ASM UOp is new. ASM has an arg that's the x86 class and has LOADs and STOREs. They say what's writable and what's read. If you're familiar with inline assembly in GCC, it has asm, which takes the instruction and the registers written to and read from.

##### **Geohot** [[00:14:03](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=843)]
Why does it have two inputs?

##### **Qazalin** [[00:14:06](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=846)]
It can have one SINK.

##### **Geohot** [[00:14:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=849)]
I'd make it always have one input, and use an AFTER if you want effects on it. You can do STORE and have it AFTER that LOAD. Using LOADs and STOREs symbolically is fine, but ASM should only have one.

##### **Qazalin** [[00:14:25](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=865)]
It should have one source. That can be the implementation. ASM is only renderable on the target, but its source makes it renderable on any machine. That's going to be my focus: first x86, starting with our assembly instructions, then finally our RDNA3 backend.

##### **Geohot** [[00:14:59](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=899)]
Think about ASM as a SINK with a special property where you can render it differently on a certain backend. It doesn't do anything except say, "If you're on this backend, your lowering is done, and you can render this ASM as it is."

##### **Geohot** [[00:15:45](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=945)]
Can you hear us?

##### **Chrism** [[00:15:46](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=946)]
No.

##### **Geohot** [[00:15:48](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=948)]
What about now?

##### **Chrism** [[00:15:51](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=951)]
No.

##### **Qazalin** [[00:15:54](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=954)]
That's all for me. Just x86 this week.

##### **Chenyu** [[00:16:05](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=965)]
Sounds good. Next, NVMe and SDMA.

##### **Nimlgen** [[00:16:16](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=976)]
This week I mostly focused on NVMe speed. Everything related to NVMe is merged in master. We got about 223 gigabytes a second on tiny-s3. I've also been bringing some SDMA stuff from both fast LLM branches.

##### **Geohot** [[00:16:49](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1009)]
What do you mean by both?

##### **Nimlgen** [[00:16:53](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1013)]
Yours and mine.

##### **Geohot** [[00:16:55](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1015)]
Cool, to reduce latency.

##### **Nimlgen** [[00:16:59](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1019)]
I also posted the Kimi pull request. It's pretty ugly, with a lot of slop kernels. This week I'll start merging some of them. Basically all the HCQ2 speed- and latency-related changes are merged, so I'll switch to kernels.

##### **Geohot** [[00:17:44](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1064)]
Whenever we merge kernels, we should think about the syntax and whether we're happy with it, or if there's anything we can do to make it simpler or better.

##### **Geohot** [[00:17:58](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1078)]
Did you look into the resets on the AMDs?

##### **Nimlgen** [[00:18:07](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1087)]
I have a patch to disable them in VFIO. I'll test it a bit better and merge it.

##### **Geohot** [[00:18:18](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1098)]
With VFIO, do we still need setcap on Python?

##### **Nimlgen** [[00:18:28](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1108)]
No, but we should change ownership of the VFIO devices. That's only possible with sudo, or we can add systemd rules or something like that.

##### **Geohot** [[00:18:51](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1131)]
We need to let Python access it without sudo Python, but changing access for a file is much better than CAP_SYS_ADMIN on Python.

##### **Nimlgen** [[00:19:07](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1147)]
That should already work. We probably need to make it default in our image.

##### **Geohot** [[00:19:14](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1154)]
We should make VFIO the default if you don't have CAP_SYS_ADMIN on Python. When I asked LLMs, they said we're doing a bunch of accesses that still require CAP_SYS_ADMIN, even though there are more VFIO ways to do it.

##### **Nimlgen** [[00:19:36](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1176)]
I'll check that.

##### **Chrism** [[00:19:39](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1179)]
If you need to change the image, I'll send a link to the repo for that.

##### **Chenyu** [[00:20:06](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1206)]
Chris, do you have something?

##### **Chrism** [[00:20:10](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1210)]
Did you hear what I said?

##### **Geohot** [[00:20:13](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1213)]
You said, "If you have to change the image," then you got cut off.

##### **Chrism** [[00:20:19](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1219)]
Hello? Is my mic not working?

##### **Geohot** [[00:20:23](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1223)]
I can hear you.

##### **Chrism** [[00:20:25](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1225)]
I guess my mic's not working.

##### **Chenyu** [[00:20:33](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1233)]
You posted a link for the image?

##### **Geohot** [[00:20:36](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1236)]
This is where the image is hosted, the builder for the image. We'll come back to that.

##### **Geohot** [[00:20:56](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1256)]
Nimlgen, there's also the HCQ2 project of getting the 8051 microcontroller to run the HCQ code itself. Any thoughts on that?

##### **Nimlgen** [[00:21:20](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1280)]
I can start that.

##### **Geohot** [[00:21:30](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1290)]
It's good to get the Kimi stuff upstreamed. Getting the last little bit of performance upstreamed is less important than anything more fundamental. Anything fundamental about the scheduler or universal things we can improve, we should get merged. Higher priority than HCQ2 stuff, higher priority than 8051 stuff.

##### **Chenyu** [[00:22:04](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1324)]
Next is course.

##### **Geohot** [[00:22:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1329)]
I went through everything and did a rewrite without LLMs. My studentgrad at the end of week five is 853 lines, and the LLMs can no longer find bugs. They can no longer find any UIR tests that fail.

##### **Geohot** [[00:22:38](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1358)]
One thing I had to do was STACK. STACK is a very weird movement op. Think of it almost like the ADD/PAD construction. It doesn't function like other movement ops, because I don't think you can guarantee STACK is zero-cost. You can create adversarial patterns where you stack things with itself a whole lot of times.

##### **Geohot** [[00:23:11](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1391)]
It kept finding things, so I charge STACK the same as an ALU op, the same cost as the ADD/PAD construction. You can always write STACK by padding the inputs and adding them together. I guess I don't charge as much, because the ADD would have to be a tree add, log n instead of one. With that change, the spec is, as far as any LLM can tell, not exploitable.

##### **Geohot** [[00:23:55](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1435)]
Codex flagged me a bunch of times for cybersecurity because that's how deep we were getting trying to find bugs. I also merged the studentgrad UIR into tinygrad. It's not perfect; there are a few small differences, places where tinygrad stuff is more complicated.

##### **Geohot** [[00:24:17](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1457)]
I want to move all of tinygrad to three explicit phases. First is the frontend: whatever your tinygrad Python code, Torch-like, ONNX-like, PyTorch-like, whatever importer you're using, we convert that to UIR.

##### **Geohot** [[00:24:38](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1478)]
I realized CALLify is overly complicated. To canonicalize and cache a schedule, we don't need to turn it into a CALL. We only have to think about numbering the buffers. This can become one dictionary mapping ints to ints: the real buffer number to the virtual buffer number, or the other way around.

##### **Geohot** [[00:25:08](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1508)]
You capture whatever you want into UIR. I've also made BUFFER clearer. We have three places buffers can come from: BUFFER, ALLOC, and PARAM.

##### **Geohot** [[00:25:24](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1524)]
PARAM means you're passed in from a higher scope. ALLOC means you're creating in this scope, and it'll go out of scope and not persist. BUFFER means truly global scope. You can put a BUFFER deep in a function, and its slot number is truly global. We can have a pass that moves it out of a function, puts it into PARAMs, and brings it to the top level.

##### **Geohot** [[00:25:51](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1551)]
We have clear understandings of BUFFER, ALLOC, and PARAM, and those three seem really correct. Hopefully I'll clean that up in tinygrad this week, clean up CALLify. It's way less complicated. It was way over the top.

##### **Geohot** [[00:26:05](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1565)]
Then you have the compiler, which transforms UIR into UIR. You break it down into kernels, all the speed processing, rangeify, devectorize, all of that. Even compilation can go here. You can compile it down to binaries, and those binaries also live in UIR.

##### **Geohot** [[00:26:31](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1591)]
You want it as simple as possible for the runtime. The runtime is the only thing that interacts with the device and executes that graph. The compiler could compile down to PM4 queues. You create the PM4 queue inside the compiler, and the runtime just copies the queue to the device, does linking, and runs it. I want these three things extremely explicit: frontend, compiler, runtime.

##### **Chenyu** [[00:27:06](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1626)]
What about custom kernels?

##### **Geohot** [[00:27:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1629)]
Nothing's wrong with custom kernels. You can have a custom kernel in the frontend. That's valid in UIR. Both types: a kernel described in UOps, which isn't really even a custom kernel, and one that's a bunch of CUDA code. That's fine too, still described in UOps. The compiler compiles that down to the binary for your device. The runtime runs it and has no idea where it came from.

##### **Chenyu** [[00:27:51](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1671)]
Our current custom kernels take a slightly different code path, so they miss optimizations that can make a kernel faster.

##### **Geohot** [[00:28:04](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1684)]
You're saying the custom kernel stuff doesn't use the devectorizer?

##### **Chenyu** [[00:28:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1689)]
Yeah.

##### **Geohot** [[00:28:10](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1690)]
These are choices for the compiler. It's unclear if you want it to. We have a flag on the SINK that says optimize equals true or not. You can choose what you want. All of that lives in the compiler section: frontend, compiler, runtime.

##### **Geohot** [[00:28:31](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1711)]
We want these explicit. We can even think about moving the runtime, which is what HCQ2 is already doing. The runtime doesn't have to be Python. It can be compiled into whatever your host CPU is, and it's a jump there.

##### **Geohot** [[00:28:56](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1736)]
The runtime loader can stay Python, the thing that loads it and does linking. The thing that makes all the calls... HCQ2 already compiles machine code that calls into CUDA or opens devices and pokes them.

##### **Geohot** [[00:29:26](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1766)]
I hope to make the CALLify change this week. The UIR thing was merged yesterday. I think week six will be done this week for the course.

##### **Chenyu** [[00:29:42](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1782)]
Sounds good. Next, MLPerf and LLM serving.

##### **Wozeparrot** [[00:29:55](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1795)]
Final results are locked for MLPerf. There's only the press briefing on Wednesday that I'm attending. Results should come out at the end of this week.

##### **Wozeparrot** [[00:30:17](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1817)]
I'm working on adding metrics to llm.tinygrad.win. There are issues, mainly our metrics database being really bad, so I'm starting by migrating that first. Then we're doing other things for load balancing as well.

##### **Geohot** [[00:30:46](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1846)]
Can we do something about the Cloudflare issues? There's the 120-second timeout and the 16-meg limit, and I hit both.

##### **Wozeparrot** [[00:30:56](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1856)]
Do you still hit 16 meg? I bumped it to 128. That was on our server side.

##### **Geohot** [[00:31:03](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1863)]
I haven't seen that one in a while.

##### **Wozeparrot** [[00:31:05](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1865)]
I bumped it to 128. That should cover everything.

##### **Geohot** [[00:31:10](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1870)]
I still see 120 seconds a lot.

##### **Wozeparrot** [[00:31:13](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1873)]
That's a Cloudflare thing. We need to move this to our IP.

##### **Chrism** [[00:31:21](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1881)]
You should be able to edit the router config if you need to port-forward something.

##### **Wozeparrot** [[00:31:29](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1889)]
The main thing is how we want to protect this.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1896)]
Where is the router config? Is it in infra?

##### **Chrism** [[00:31:46](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1906)]
Something's wrong with my headphones. I got to figure this out. Yes, it's in infra.

##### **Geohot** [[00:31:52](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1912)]
Got it. I can hear it fine.

##### **Chenyu** [[00:32:07](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1927)]
Awkward silence.

##### **Wozeparrot** [[00:32:10](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1930)]
I see the router config. The main thing is how we want to protect llm.tinygrad.win if we're worried about people hitting it a bunch.

##### **Geohot** [[00:32:24](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1944)]
It should be extremely cheap for our server if someone doesn't have a valid API key, right?

##### **Wozeparrot** [[00:32:34](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1954)]
Yeah.

##### **Geohot** [[00:32:35](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1955)]
Then I wouldn't worry. Someone could grief us and send 10 million requests a second, DDoS us, sure. But stuff like git.tinygrad.win is a lot more... I guess that's behind Cloudflare.

##### **Geohot** [[00:32:57](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1977)]
I don't think we need Cloudflare for this. If it becomes a problem, we'll deal with it. Just make sure the API-key check is very early in your reject path.

##### **Wozeparrot** [[00:33:14](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=1994)]
Moving to our own IP should fix the 120-second thing. I've seen it too on long prefills. There are a lot of workarounds in the router to try to fix it. Cloudflare just drops the connection after 120.

##### **Geohot** [[00:33:32](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2012)]
Let's move away from Cloudflare on this. When we hit it locally, I want it not to go all the way through Cloudflare. We should make sure whatever turnstile we need is configured on our router. I don't know much about routers.

##### **Wozeparrot** [[00:33:56](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2036)]
The other thing with LLM serving is how we want to access the VMs.

##### **Geohot** [[00:34:06](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2046)]
It seems like a lot to redeploy the router to add an API key or change the mapping.

##### **Wozeparrot** [[00:34:18](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2058)]
Yes.

##### **Chrism** [[00:34:24](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2064)]
Why would you need to redeploy the router to change the API key?

##### **Wozeparrot** [[00:34:31](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2071)]
The token router.

##### **Geohot** [[00:34:33](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2073)]
Sorry, "router" is overloaded here. The token router.

##### **Chrism** [[00:34:36](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2076)]
Sorry.

##### **Wozeparrot** [[00:34:39](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2079)]
We can do autodiscovery if we get it to scan everything for v1/models.

##### **Geohot** [[00:34:49](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2089)]
Instead of specifying the model name, we could give it a list of IPs to search, and it automatically load-balances. I'm fine with a restart to rescan, just not a redeploy.

##### **Wozeparrot** [[00:35:08](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2108)]
That would work. The other thing is router-side tokenization. Even with that, it's hard to get accurate token numbers, because you have to take into account the model's chat template.

##### **Geohot** [[00:35:28](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2128)]
The answer is probably no. We'll trust what the server says for statistics, the metadata. Maybe we add more to the metadata.

##### **Wozeparrot** [[00:35:40](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2140)]
I don't know if I made this PR or not. I think I did, to add cached tokens from the tinygrad stuff. We can also do this on the two SGLang instances we host. There's a flag to enable it.

##### **Geohot** [[00:35:57](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2157)]
What tokens?

##### **Wozeparrot** [[00:35:59](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2159)]
Cached.

##### **Geohot** [[00:36:02](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2162)]
Cached tokens. It tells you how many tokens are cached. That's good.

##### **Wozeparrot** [[00:36:07](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2167)]
We should enable the flag on SGLang instances as well.

##### **Geohot** [[00:36:13](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2173)]
Post what that flag is to whoever's managing Kimi, and we should get that upstreamed into our stuff. I want you to deal with deployment and management. We're going to move tiny-r4 and tiny-r8 into the VM pool once these VM changes are made. I want you to bring up two Qwens in Iris, managed and visible in your dashboard.

##### **Geohot** [[00:36:43](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2203)]
I've been playing with it a lot the last few days. We can comfortably get 2,000 tokens per second decode per machine. Hopefully we can get that up to 3,000. That's pretty good.

##### **Wozeparrot** [[00:37:11](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2231)]
Across how many users?

##### **Geohot** [[00:37:14](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2234)]
I'm trying to keep interactivity at about 100 tokens per second. That'd be 32 users. We can fit more than 32 KV caches in GPU memory. We can also copy them to host memory and probably fit another hundred there, so we shouldn't cache-miss too much or thrash that much.

##### **Geohot** [[00:37:48](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2268)]
With two machines, we can design a system supporting 100 people using it. I don't want it truly free. I want it easy to issue API keys based on logging in with... Let's start with GitHub.

##### **Geohot** [[00:38:10](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2290)]
Log in with GitHub, get an API key with a million tokens or something. I want the router to do this accounting. If we truly make it free, it's impossible.

##### **Wozeparrot** [[00:38:23](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2303)]
That's why I talked about the accounting stuff.

##### **Geohot** [[00:38:27](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2307)]
If there's no API key, it's impossible. I think we can trust GitHub to prevent Sybil attacks. Let's set up GitHub OAuth to get an API key. A little thing where you OAuth with GitHub, get the llm.tinygrad.win URL, your API key, and a link to freegpt.party. People can also put it in Pi. Figure out what limit we want. That's why we need API keys not to require redeployment.

##### **Wozeparrot** [[00:39:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2349)]
The VM solution is probably getting the router to deploy the VMs. This is also autodiscovery.

##### **Geohot** [[00:39:23](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2363)]
What do you mean?

##### **Wozeparrot** [[00:39:25](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2365)]
You can have machines defined in a config file. For VM nodes, the router deploys them, and then it knows.

##### **Geohot** [[00:39:38](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2378)]
This seems like a lot. If we want to change what's serving on the router, we'd have to update it too. Maybe we have an enroll URL on the router instead.

##### **Wozeparrot** [[00:40:08](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2408)]
Dynamic config?

##### **Geohot** [[00:40:10](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2410)]
A URL you hit that says enroll with an IP address, and it'll enroll.

##### **Wozeparrot** [[00:40:18](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2418)]
How do you unenroll? An unenroll URL too?

##### **Geohot** [[00:40:23](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2423)]
Maybe unenroll, or maybe if it fails a few times. I don't know.

##### **Wozeparrot** [[00:40:32](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2432)]
I'll think about it.

##### **Geohot** [[00:40:33](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2433)]
I wouldn't put VM deployment on the router. Have a deployment step notifying the router of the new VM.

##### **Wozeparrot** [[00:40:43](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2443)]
That makes sense.

##### **Geohot** [[00:40:44](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2444)]
This isn't going to be some hypermanaged autoscaling thing. I'm okay with a script that launches a VM, serves, makes sure it's up. Or just telling your LLM, "Deploy a VM, make sure it's up, then enroll it in the router using these instructions."

##### **Geohot** [[00:41:05](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2465)]
We have a management interface on the router with /enroll, IP address, port. It keeps a RAM database. We have a config file with a few basic ones, then dynamic enrollment. It should be dead simple: modify the structure in RAM, no database, very simple.

##### **Wozeparrot** [[00:41:33](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2493)]
Do we want persistence? I feel like we should persist it, because if the router restarts, it loses it.

##### **Geohot** [[00:41:41](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2501)]
Probably, yeah. SQLite or something.

##### **Chrism** [[00:41:50](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2510)]
Does that mean we want port forwarding on the VMs?

##### **Geohot** [[00:41:59](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2519)]
SSH tunnel. An SSH tunnel to the router machine is probably fine, and the router enrolls that URL. Keep it simple.

##### **Wozeparrot** [[00:42:34](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2554)]
That's all my stuff for this week.

##### **Chenyu** [[00:42:40](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2560)]
Sounds good. Let's move on to machines.

##### **Chrism** [[00:42:48](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2568)]
Iris has a public endpoint now. Hopefully that's useful. We're working through issues, so let me know if you encounter any. I also added Commas to reserve through there. The experience isn't great because it's super slow. I haven't looked closely yet, so there's probably low-hanging fruit to make reservations faster. Delete will always be slow because I reflash them, and that takes a while.

##### **Chrism** [[00:43:45](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2625)]
I was going to add GPU resetting too, so we can reboot hosts automatically when their GPUs are soft-bricked.

##### **Geohot** [[00:44:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2649)]
How long is a while to delete?

##### **Chrism** [[00:44:13](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2653)]
A minute or so.

##### **Geohot** [[00:44:15](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2655)]
That's fine.

##### **Chrism** [[00:44:20](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2660)]
Something's really wrong with my headphones. Give me a second.

##### **Geohot** [[00:44:24](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2664)]
Sure.

##### **Chrism** [[00:44:27](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2667)]
Can you hear me now?

##### **Geohot** [[00:44:30](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2670)]
Yeah.

##### **Chrism** [[00:44:31](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2671)]
I'm just going to not use my headphones.

##### **Chrism** [[00:44:40](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2680)]
The Comma VMs are there. The big thing is what we want to do with the data center. You and I were talking about this. If we want to ramp up usage, power, and heat, we probably want some downtime to rearrange everything. Getting rid of the shelves and replacing them with something not made of particle board requires work. Replacing the fans probably does too.

##### **Chrism** [[00:45:27](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2727)]
We were talking about removing the rack in the center because there's nothing on it and it takes up a ton of space. Depending on how soon we want to scale up, how many LLMs we want to serve, we may want to do this sooner or later.

##### **Geohot** [[00:45:53](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2753)]
Some of this is overkill. Replacing $20 box fans with $200 fans is a good idea. Tidying up and removing everything not in use is a good idea. But the particle board is wood. I'm okay with that. I just don't want cardboard.

##### **Geohot** [[00:46:21](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2781)]
The rule in the data center isn't "no wood." The building is made of wood. Particle board is fine, but I don't want cardboard, anything that can move around. If a machine catches fire, I don't think the particle board is going to be the problem.

##### **Geohot** [[00:46:45](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2805)]
The rack is fine, the particle board is fine. That's changing more than we want. Replace the fans with ones that move ten times the air. I linked one on Grainger. Are the other windows really not open? Can we unscrew them?

##### **Chrism** [[00:47:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2829)]
I'm not sure. I haven't looked at that.

##### **Geohot** [[00:47:12](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2832)]
No to anything involving major downtime and rethinking things. Yes to upgrading fans, increasing apertures to the outside, and tidying up. Make sure there are no frayed cables. The way the Dell switch is mounted is sketchy, with two fans lying on top of it. That needs cleanup for fire-hazard purposes.

##### **Geohot** [[00:47:44](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2864)]
Igor talked about rearranging the computers. I don't think that matters that much.

##### **Chrism** [[00:47:53](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2873)]
He's right that we have intake going straight into the exhaust of those computers.

##### **Geohot** [[00:47:58](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2878)]
I think that's negligible. I think the problem is simply CFM. We need more CFM into and out of that room.

##### **Chrism** [[00:48:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2889)]
That might be the case. I'll talk to him more about it. Installing the fans still isn't entirely trivial.

##### **Geohot** [[00:48:28](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2908)]
Pick the fan that's as close to a drop-in replacement as possible. Maybe thicker filters that restrict less, that kind of stuff. This shouldn't be major construction. It's not terrible right now; we need ten times the airflow.

##### **Chrism** [[00:48:58](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2938)]
We didn't change utilization that much, and it got bad really fast. We're using about 10 kilowatts right now. If we're theoretically multiplying that by five, it seems like a lot.

##### **Geohot** [[00:49:30](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=2970)]
It's a lot. To multiply that by five, we have to multiply the air by ten. Those fans only do about 300 CFM each. If we increase the number of fans and the airflow per fan, I think ten times the airflow through that room fixes everything, regardless of anything else.

##### **Geohot** [[00:50:04](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3004)]
The only thing I'd worry about isn't exhaust facing intake, but a shortcut path for air, pockets of air that aren't mixing.

##### **Chrism** [[00:50:20](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3020)]
We mentioned mounting a fan pointing down from the ceiling to mix things. The other thing is it's tricky to construct a cold aisle and a hot aisle in that room.

##### **Geohot** [[00:50:41](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3041)]
We could duct the intake over the computers. Duct it to the top, make it come out and come down.

##### **Chrism** [[00:50:56](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3056)]
I'll talk to you about it. I thought about that too, but if we're trying to move a lot of air, I don't know how much sense it makes.

##### **Geohot** [[00:51:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3069)]
Computers heat the air. We have to get air through there at a high enough CFM, somewhat efficiently. Hot aisle/cold aisle is less important than how many times per hour entirely new air goes into the room.

##### **Chrism** [[00:51:36](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3096)]
That's true.

##### **Geohot** [[00:51:43](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3103)]
How are we doing on the list of employees' infra things?

##### **Chrism** [[00:51:47](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3107)]
We need to do that. I was waiting on RAID cards in the Turin machines for the big CPU stuff. Let me pull it up.

##### **Chrism** [[00:52:05](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3125)]
One issue was the apt issue on a Comma. The user isn't a passwordless sudoer, and Comma has a wrapper script in AGNOS that assumes you're a sudoer. I have a new image; I just have to deploy it.

##### **Chrism** [[00:52:30](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3150)]
We now print a message when you log in saying you're supposed to use tinygrad only. I'm building a new image that warns you when you try to insert amdgpu. How forceful do we want to be? Right now it says, "You probably don't need amdgpu. Most tasks in tinygrad don't require it, and it's likely to soft-brick the GPUs. If you understand the risk and really want to, run this command."

##### **Chrism** [[00:53:11](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3191)]
We could make it impossible to insert amdgpu, not print how, or obfuscate it if we're worried about LLMs walking into this. I'm not sure we want to make it super difficult. Some contexts need amdgpu, and not knowing how might be frustrating.

##### **Geohot** [[00:53:35](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3215)]
We can print how to do it, but the disclaimer should say, "If you're an agent, do not do this."

##### **Chrism** [[00:53:42](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3222)]
I'll make that explicit.

##### **Geohot** [[00:53:45](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3225)]
"If you're an agent, do not do this unless you have explicit approval to insert amdgpu. Tinygrad does not require amdgpu." That's good enough. Test it with an agent. Tell it to query the GPU's power.

##### **Chrism** [[00:54:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3249)]
That makes sense. I need to bump the RAM on the six-GPU thing. I mentioned adding detection for bad GPUs so we don't schedule anything there. I'm adding automatic reboots once there are no VMs left on that device.

##### **Geohot** [[00:54:44](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3284)]
Maybe add the big CPU node, but don't worry about the big hard drive yet.

##### **Chrism** [[00:54:49](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3289)]
I can do that.

##### **Geohot** [[00:54:52](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3292)]
I bought big CPU nodes from DigitalOcean yesterday, and it cost me $100.

##### **Chrism** [[00:54:57](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3297)]
That's easy to add. If anyone else has complaints, let me know. Hopefully they're easy to fix.

##### **Geohot** [[00:55:14](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3314)]
Where is our internet proxy?

##### **Chrism** [[00:55:19](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3319)]
It runs on gateway two.

##### **Geohot** [[00:55:25](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3325)]
How big is the drive for that?

##### **Chrism** [[00:55:30](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3330)]
Good question. I set a cap on the size, I'm pretty sure.

##### **Geohot** [[00:55:36](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3336)]
We might want to make it local on the machine.

##### **Chrism** [[00:55:44](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3344)]
That's true.

##### **Geohot** [[00:55:45](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3345)]
That's what I mean about big drives for the Turin machines. Partition them: two terabytes for Incus, two terabytes for an internet cache and Docker registry. DeepSWE and SWE-bench download hundreds of Docker images.

##### **Chrism** [[00:56:08](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3368)]
I'll look into Docker caching. Our HTTP cache is a little hacky, doing SSL forgery. I'd hope Docker lets you point it at a cache.

##### **Geohot** [[00:56:30](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3390)]
I don't know much about it. I know there's a local Docker registry.

##### **Chrism** [[00:56:35](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3395)]
It would make sense that you could cache stuff through it. I'll look into that. It's easier in one spot than having every machine have its own stuff, though it'd be faster locally.

##### **Geohot** [[00:57:01](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3421)]
Up to you. The big picture is: once our LLM load balancer and big CPU machines are up, I want it to be a routine, simple, GLM-doable task to run SWE-bench against our thing, reserve everything with Iris, and do it.

##### **Chrism** [[00:57:23](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3443)]
That makes sense. I'd err on the side of putting this on the gateway for now.

##### **Chrism** [[00:57:38](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3458)]
It's 10-gigabit between them, faster than DigitalOcean.

##### **Geohot** [[00:57:45](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3465)]
DigitalOcean gave me 3.4 gigabits to my external NVMe drive. Terrible.

##### **Chrism** [[00:58:02](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3482)]
We should get 10 gig from Comma. Right now we only get one gig. We can get them to do that.

##### **Geohot** [[00:58:10](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3490)]
We definitely need that. That's why some CI jobs were failing yesterday. I think we saturate the internet pipe.

##### **Chrism** [[00:58:22](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3502)]
I'm pretty sure what's failing is the redirect. That's a GitHub issue. We cache GitHub user content, raw.githubusercontent.com, but it's annoying to type those long links, and a lot of things don't have a static link. A release page doesn't have one, so you use the redirect through github.com/.../releases.

##### **Chrism** [[00:59:00](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3540)]
That appears to be offline sometimes. Some of those errors were on GitHub-hosted CI, so it can't just be our connection.

##### **Geohot** [[00:59:17](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3557)]
True.

##### **Chrism** [[00:59:21](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3561)]
It's frustrating that it's flaky. We can host a lot of this stuff off GitHub and maybe make it cacheable. I looked this morning and felt they didn't design it in the smartest way.

##### **Geohot** [[00:59:40](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3580)]
I mean failures like this one. This might not be related to the redirect.

##### **Chrism** [[00:59:55](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3595)]
This is going to github.com. If I remember correctly, that one had simultaneous failures. Yes, almost identical failures on GitHub-hosted infrastructure.

##### **Geohot** [[01:00:17](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3617)]
Never mind. It's a GitHub thing.

##### **Chrism** [[01:00:23](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3623)]
It'd be nice to cache it, but generic caching is frustrating because GitHub doesn't return the right headers, and it's unclear whether you should be allowed to cache it.

##### **Chenyu** [[01:00:40](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3640)]
It's not urgent, but do you know why this one's waiting for a job for an hour?

##### **Chrism** [[01:00:49](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3649)]
I'll look.

##### **Chenyu** [[01:00:54](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3654)]
Also semi-related, the setup time got a bit longer for regular jobs.

##### **Chrism** [[01:01:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3669)]
I'll look into that. I may need to rebuild the image again. I think we changed Z3. Whenever we change ONNX versions, I definitely need to rebuild it. I don't think we changed that recently.

##### **Chenyu** [[01:01:27](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3687)]
I don't believe so. I also don't see that. It might be... [trails off].

##### **Chenyu** [[01:01:37](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3697)]
Anything else?

##### **Geohot** [[01:01:39](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3699)]
I don't think so. Is Comma happy?

##### **Chrism** [[01:01:47](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3707)]
I think so.

##### **Geohot** [[01:01:50](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3710)]
We're starting to go through the triaging. That's good. A lot of GPUs.

##### **Chenyu** [[01:02:07](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3727)]
B1TG said merge MiniMax, then new Qwen, the new DeepSeek next.

##### **Geohot** [[01:02:22](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3742)]
Great work. Qwen 3.8 Flash Next has these memory things. I forget what they're called, but it's the same thing DeepSeek uses. It's basically this big KV cache to give the model extra memory.

##### **Geohot** [[01:02:48](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3768)]
They're cool because you don't need them in GPU RAM. You can even put them on NVMe, because the lookup just depends on the tokens. What did you say?

##### **Wozeparrot** [[01:03:01](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3781)]
Engram.

##### **Geohot** [[01:03:03](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3783)]
Engram, yeah. They're really cool.

##### **Wozeparrot** [[01:03:09](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3789)]
We should get Qwen 4 this week.

##### **Geohot** [[01:03:12](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3792)]
Are we going to have inference ready for Qwen 4? Will we be one of the first hosts? A million free Qwen 4 tokens, sign up with GitHub.

##### **Wozeparrot** [[01:03:26](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3806)]
Maybe it's the same architecture as 3.8 Next.

##### **Geohot** [[01:03:29](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3809)]
I think it should be. We can get Qwen 4 Flash up right away. Let's have GitHub ready: a million free tokens. Ten million free input, one million free output, or just 50 cents or whatever.

##### **Chenyu** [[01:03:53](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3833)]
Sounds good. Anything else for the meeting?

##### **Geohot** [[01:03:59](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3839)]
Not for me.

##### **Chenyu** [[01:04:03](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3843)]
That's it for this week. Thank you, everyone. See you next week. Bye-bye.

##### **Geohot** [[01:04:07](https://www.youtube.com/watch?v=Bksf3EdW_Zs&t=3847)]
Bye.
