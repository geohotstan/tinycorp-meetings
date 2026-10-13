# 2026-10-13 Meeting

- NOTE: missing company update this recording because I messed up...

### Meeting Agenda

**Time:** new meeting #41, 10/13 12pm Hong Kong time
- company update
- CALL, UIR, course
- MLPerf
- HCQ2
- CI
- assembly
- bounties, Comma, RDNA

### Audio

[Youtube Link](https://www.youtube.com/watch?v=f1g9GenfTr8)

### Highlights

- **[MLPerf Submission](#wozeparrot-000033)**: Wozeparrot reviewed all logging/package checker; final times are ready, branches will be pushed to upstream tinygrad and linked in READMEs, and he will attend the review meeting/media day.
- **[AMD State-of-the-Art](#geohot-000115)**: Geohot notes the MLPerf scores are state-of-the-art for AMD, but not yet NVIDIA-beating; NVIDIA nitpicking is expected once tinygrad beats them.
- **[Carnegie Mellon Course](#geohot-000420)**: Spring course starts Jan 20; Geohot is building studentgrad reference compiler; work surfaced effect-folding rules, removed FLIP, and is testing whether END/STAGE can merge.
- **[UIR/CALL Buffer Model](#geohot-000605)**: Three buffer forms: BUFFER is a global slot, buffers inside CALL are static, and ALLOC is function-scoped; CALL semantics are being discussed in assembly/UIR.
- **[Qazalin Emulator / Clang JIT](#qazalin-001028)**: Qazalin's branch replaces the old emulator with lifted GPU dispatch in one C program; runtime is faster, but creation/compile is slower; libclang JIT/autogen discussed to avoid recompiling helpers.
- **[STACK and Symbolic Optimization](#chenyu-001604)**: Chenyu is replacing PAD with STACK; investigating symbolic analysis for STACK/WHERE such as modulo/bit constraints and LLVM known-bits-like passes; STACK preferred over PAD/ADD, CAT still scary.
- **[HCQ2 Cleanups](#nimlgen-002213)**: HCQ2 gains proper error handling/timeouts, ~23 GB/s disk reads on G3 RAID, and a HIP backend reusing CUDA; further cleanups planned.
- **[CI Self-Hosting](#chrism-003031)**: Collaborator CI is self-hosted on data-center machines, letting tinycorp cancel Namespace; queue times are slightly higher (~20s vs ~12s) awaiting an upstream fix.
- **[VM/CI Hardware Plans](#geohot-003506)**: Plan to retire G machines, move tinybox access to VM access, use tinybox talls with many 3080s for students, and share VMs with CI.
- **[Comma Fork](#chrism-003925)**: Comma is currently on its own tinygrad fork; the team wants to discourage forking and get their PRs merged/upstream, with Chestnut/comma 3X testing available.
- **[Self-Hosting LLMs / AMD](#geohot-004139)**: Goal to move tinycorp LLMs off SGLang onto tinygrad, add GLM-5.3, target tinyamd2 and InferenceX by SemiAnalysis; focus on 300s over 350s.
- **[Bounties to Merge](#geohot-004437)**: Pending bounties include buffers/args in any order, Ocelot CUDA 11/12 support, and Qualcomm emulator; Geohot/Qazalin to help merge and pay out.
- **[LLM Server/Cache](#geohot-004651)**: Multithreaded server PR is mostly fine but logging is ugly; variable-batch decode is the priority, enabling speculative decoding; LRU cache likely sufficient.

### Transcript
##### **Chenyu** [[00:00:00](https://www.youtube.com/watch?v=f1g9GenfTr8&t=0)]
Okay, let's start. Since it's the MLPerf deadline, we'll start with MLPerf submission. What's our current state? Everything good?

##### **Wozeparrot** [[00:00:07](https://www.youtube.com/watch?v=f1g9GenfTr8&t=7)]
Yes. Give me a sec, grabbing all the...

##### **Chenyu** [[00:00:13](https://www.youtube.com/watch?v=f1g9GenfTr8&t=13)]
Can you post the final times or our submission status somewhere?

##### **Wozeparrot** [[00:00:20](https://www.youtube.com/watch?v=f1g9GenfTr8&t=20)]
Yeah, those are our final times for everything.

##### **Geohot** [[00:00:25](https://www.youtube.com/watch?v=f1g9GenfTr8&t=25)]
Are we sure we're not going to get flagged, like we didn't do anything wrong?

##### **Wozeparrot** [[00:00:33](https://www.youtube.com/watch?v=f1g9GenfTr8&t=33)]
I went over everything with GPT, and it seems good. I also read over the logging, and it seems good. Technically, in our previous submissions we only submitted the MLLOG lines, but they want all logging lines. This time I did that.

##### **Chenyu** [[00:00:51](https://www.youtube.com/watch?v=f1g9GenfTr8&t=51)]
Right, okay.

##### **Geohot** [[00:00:52](https://www.youtube.com/watch?v=f1g9GenfTr8&t=52)]
If you're going through it with a good LLM and it says it's good, then it's probably good.

##### **Wozeparrot** [[00:00:57](https://www.youtube.com/watch?v=f1g9GenfTr8&t=57)]
It passes the package checker. The only thing is, it's unclear what people might bring up. Before, we didn't really submit state-of-the-art scores, so I'm assuming people wouldn't care that much. Now that we're submitting state-of-the-art scores, people might look more into it.

##### **Geohot** [[00:01:15](https://www.youtube.com/watch?v=f1g9GenfTr8&t=75)]
State of the art for AMD. We haven't beaten NVIDIA yet. When we beat NVIDIA, they're going to nitpick.

##### **Chenyu** [[00:01:29](https://www.youtube.com/watch?v=f1g9GenfTr8&t=89)]
How much of this is on master?

##### **Wozeparrot** [[00:01:33](https://www.youtube.com/watch?v=f1g9GenfTr8&t=93)]
I've been working on getting the GPT-OSS stuff on master, but right now it's four separate branches, one for each submission. I wrote READMEs because they want instructions for running the code. They link to a commit and say which branch to clone. I'm hoping that's okay; they didn't really say. We can't push the entire repo into the submission because they have a check for large files.

##### **Geohot** [[00:02:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=124)]
We have large files?

##### **Wozeparrot** [[00:02:06](https://www.youtube.com/watch?v=f1g9GenfTr8&t=126)]
They check that your benchmark source-code submission folder is under a specific size. I don't think they want people pushing all the code they use into that folder, just to keep the repo size small.

##### **Chenyu** [[00:02:26](https://www.youtube.com/watch?v=f1g9GenfTr8&t=146)]
That makes sense. There's no way you upload your whole Torch version with all the NVIDIA stuff.

##### **Geohot** [[00:02:34](https://www.youtube.com/watch?v=f1g9GenfTr8&t=154)]
Oh yeah. AMD's largest package is [unclear].

##### **Wozeparrot** [[00:02:41](https://www.youtube.com/watch?v=f1g9GenfTr8&t=161)]
I checked other people's submissions, and they just seem to upload their .sh configs.

##### **Geohot** [[00:02:48](https://www.youtube.com/watch?v=f1g9GenfTr8&t=168)]
Just make sure we have that commit pinned in a tag or something that's easy for people to get to.

##### **Wozeparrot** [[00:02:55](https://www.youtube.com/watch?v=f1g9GenfTr8&t=175)]
I'll push all those branches to upstream tinygrad, and then they're all linkable. That should be good.

##### **Geohot** [[00:03:08](https://www.youtube.com/watch?v=f1g9GenfTr8&t=188)]
Great, sounds good. You'll be attending the review meeting and stuff?

##### **Wozeparrot** [[00:03:14](https://www.youtube.com/watch?v=f1g9GenfTr8&t=194)]
Yes.

##### **Chenyu** [[00:03:16](https://www.youtube.com/watch?v=f1g9GenfTr8&t=196)]
Cool. Also do the media-day thing when that comes around.

##### **Geohot** [[00:03:21](https://www.youtube.com/watch?v=f1g9GenfTr8&t=201)]
Let's actually do some media this time. We have good times, and we're proud of them. We want Huawei to be like, 'Wow, they got good times. They could get good times with Ascend accelerators.'

##### **Chenyu** [[00:03:42](https://www.youtube.com/watch?v=f1g9GenfTr8&t=222)]
We won't know until the review starts, after the deadline. We don't know anyone else's scores yet.

##### **Geohot** [[00:03:48](https://www.youtube.com/watch?v=f1g9GenfTr8&t=228)]
I'd be interested to see if our stuff stays the best for AMD.

##### **Wozeparrot** [[00:03:56](https://www.youtube.com/watch?v=f1g9GenfTr8&t=236)]
We should. I think the deadline is the end of this week.

##### **Geohot** [[00:03:59](https://www.youtube.com/watch?v=f1g9GenfTr8&t=239)]
Yeah, it's this week.

##### **Wozeparrot** [[00:04:01](https://www.youtube.com/watch?v=f1g9GenfTr8&t=241)]
Cool. We should know by next week.

##### **Chenyu** [[00:04:03](https://www.youtube.com/watch?v=f1g9GenfTr8&t=243)]
Cool, sounds good. Anything else?

##### **Wozeparrot** [[00:04:08](https://www.youtube.com/watch?v=f1g9GenfTr8&t=248)]
Nope.

##### **Chenyu** [[00:04:11](https://www.youtube.com/watch?v=f1g9GenfTr8&t=251)]
Okay, let's move on. Scroll up a bit. Course?

##### **Geohot** [[00:04:20](https://www.youtube.com/watch?v=f1g9GenfTr8&t=260)]
I don't know what we had last week on this, but we're teaching a course at Carnegie Mellon for the spring semester. The start date is January 20th. I've been working on the reference compiler all week, called studentgrad. There's a lot of delicious complexity, a lot of great bugs the students are going to write. I had the LLMs mining for bugs, and it brought up a ton of discussions about subtlety in tinygrad.

##### **Geohot** [[00:04:50](https://www.youtube.com/watch?v=f1g9GenfTr8&t=290)]
For example, if you have a WHERE that has effects on a branch, are you allowed to fold it? If it's like true ? 1 : STORE/AFTER, are you allowed to fold the WHERE so that the STORE/AFTER goes away? What we've decided is no. We have to be careful about preserving all effects, because it's the only thing that makes sense. You can have 'won't execute' and 'will execute,' but you can't have 'will execute contingent on how good your automatic folder is,' on how good your symbolic patterns are. That's not acceptable. I'm working on that.

##### **Geohot** [[00:05:42](https://www.youtube.com/watch?v=f1g9GenfTr8&t=342)]
We got rid of FLIP as a result of this work. I'm working on merging END and STAGE now, seeing if they're actually the same. I think they kind of are. Nothing's really new with CALL. CALL is the same. Do we have that one CALL?

##### **Chenyu** [[00:06:02](https://www.youtube.com/watch?v=f1g9GenfTr8&t=362)]
CALL we can discuss in assembly.

##### **Geohot** [[00:06:05](https://www.youtube.com/watch?v=f1g9GenfTr8&t=365)]
Oh, that CALL. I want everyone to understand the three ways buffers can exist. They can exist as BUFFER, which is global: a slot is a global slot. Buffers can also be inside CALLs. When they're inside CALLs, think of them as equivalent to static in C. Then you have ALLOC, equivalent to writing int a[4] inside a C function: it's scoped to that function. Don't worry whether it lives on the stack or heap; those are implementation details. They're implementation details in C too. Does anything require it to be on the stack?

##### **Qazalin** [[00:06:48](https://www.youtube.com/watch?v=f1g9GenfTr8&t=408)]
Yeah, a little bit.

##### **Geohot** [[00:06:50](https://www.youtube.com/watch?v=f1g9GenfTr8&t=410)]
We have BUFFER, ALLOC, and PARAM. It's important to understand those three things. That's kind of it on that. For UIR, we're still working through some syntax things. We got rid of all the commas yesterday. Square brackets mean STACK. We're debating what the scoping syntax is. It looks kind of like an LLVM, OCaml, assembly-list kind of thing.

##### **Chenyu** [[00:07:25](https://www.youtube.com/watch?v=f1g9GenfTr8&t=445)]
Great. Okay, sounds good. We'll probably use Wozeparrot for experiments to see if the course format is good.

##### **Geohot** [[00:07:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=458)]
Do you have any comments on how courses have changed with AI?

##### **Wozeparrot** [[00:07:45](https://www.youtube.com/watch?v=f1g9GenfTr8&t=465)]
My current courses are meh.

##### **Chenyu** [[00:07:51](https://www.youtube.com/watch?v=f1g9GenfTr8&t=471)]
It's not about your perception of a course. It's other people: how do they interact with the course?

##### **Geohot** [[00:07:58](https://www.youtube.com/watch?v=f1g9GenfTr8&t=478)]
Does everyone just cheat and use AI? That's my understanding of what school is now.

##### **Wozeparrot** [[00:08:02](https://www.youtube.com/watch?v=f1g9GenfTr8&t=482)]
Yeah, basically.

##### **Chenyu** [[00:08:05](https://www.youtube.com/watch?v=f1g9GenfTr8&t=485)]
We were debating how to design this course so that the AI next January won't pass, and it sounds very difficult.

##### **Wozeparrot** [[00:08:15](https://www.youtube.com/watch?v=f1g9GenfTr8&t=495)]
It is very difficult.

##### **Geohot** [[00:08:18](https://www.youtube.com/watch?v=f1g9GenfTr8&t=498)]
To be fair, I had Claude run all night last night in a loop of finding tests and fixing them. It added a hundred lines to the repo. Then I went through the tests and fixed it with five lines.

##### **Chenyu** [[00:08:35](https://www.youtube.com/watch?v=f1g9GenfTr8&t=515)]
Who's going to grade that? Another AI?

##### **Geohot** [[00:08:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=518)]
Fundamentally, there's a question of what's the shortest thing. Once the course is done, I'm going to have the AIs actually do this: can you get something that passes in 500 lines?

##### **Chenyu** [[00:08:50](https://www.youtube.com/watch?v=f1g9GenfTr8&t=530)]
A big percentage of the grade is style.

##### **Wozeparrot** [[00:08:55](https://www.youtube.com/watch?v=f1g9GenfTr8&t=535)]
I find that's the easiest. I wrote a challenge for hiring at my robotics club, and the AIs just write terrible solutions. If you look over it, it's very easy to tell that no human wrote this or even touched it.

##### **Geohot** [[00:09:13](https://www.youtube.com/watch?v=f1g9GenfTr8&t=553)]
Yeah. I ran through the whole course with GLM, and funny enough, GLM was the best at it. I do like GLM's style.

##### **Wozeparrot** [[00:09:27](https://www.youtube.com/watch?v=f1g9GenfTr8&t=567)]
GLM's style is very good.

##### **Geohot** [[00:09:29](https://www.youtube.com/watch?v=f1g9GenfTr8&t=569)]
GLM's style is very good. [Unclear comparison with another model.]

##### **Qazalin** [[00:10:28](https://www.youtube.com/watch?v=f1g9GenfTr8&t=628)]
If you look at the source code, it's lifted the entire dispatch of the GPU. At the top, G is your RANGE in the main function. That's your G, and that's your L.

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=f1g9GenfTr8&t=648)]
Where's my G and my L?

##### **Qazalin** [[00:10:50](https://www.youtube.com/watch?v=f1g9GenfTr8&t=650)]
G is the top one, the range numbered two.

##### **Geohot** [[00:10:55](https://www.youtube.com/watch?v=f1g9GenfTr8&t=655)]
Oh, that's G. Okay.

##### **Qazalin** [[00:10:57](https://www.youtube.com/watch?v=f1g9GenfTr8&t=657)]
Then four is L, and that's the for loop inside each thread.

##### **Geohot** [[00:11:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=664)]
What is this, IP?

##### **Qazalin** [[00:11:07](https://www.youtube.com/watch?v=f1g9GenfTr8&t=667)]
IP is the address. It reads the address of the instruction to get the registers. This is legacy from the old emulator. I haven't changed it yet, but it's an easy refactor to switch to STACK.

##### **Geohot** [[00:11:23](https://www.youtube.com/watch?v=f1g9GenfTr8&t=683)]
Okay, that's not too bad. Does this replace the old emulator?

##### **Qazalin** [[00:11:27](https://www.youtube.com/watch?v=f1g9GenfTr8&t=687)]
It does in my branch.

##### **Geohot** [[00:11:30](https://www.youtube.com/watch?v=f1g9GenfTr8&t=690)]
How much slower is it?

##### **Qazalin** [[00:11:31](https://www.youtube.com/watch?v=f1g9GenfTr8&t=691)]
It's currently timing out, but I'm going through it and fixing it. Runtime is significantly faster because it's one C program. It's slower to create and compile.

##### **Geohot** [[00:11:47](https://www.youtube.com/watch?v=f1g9GenfTr8&t=707)]
What's slower, creating or compiling?

##### **Qazalin** [[00:11:50](https://www.youtube.com/watch?v=f1g9GenfTr8&t=710)]
I fixed compilation in that branch. It has some GPT slop to make a JIT.

##### **Geohot** [[00:11:56](https://www.youtube.com/watch?v=f1g9GenfTr8&t=716)]
I bet if you get rid of all the inlines...

##### **Qazalin** [[00:11:58](https://www.youtube.com/watch?v=f1g9GenfTr8&t=718)]
Exactly. It has a custom hand-rolled Clang JIT that does this.

##### **Geohot** [[00:12:06](https://www.youtube.com/watch?v=f1g9GenfTr8&t=726)]
I have that in one of mine. We need to fix the CPU runtime; we'll talk about that. Maybe we should add it back to HCQ2.

##### **Qazalin** [[00:12:14](https://www.youtube.com/watch?v=f1g9GenfTr8&t=734)]
I think it's a generic thing we need.

##### **Geohot** [[00:12:16](https://www.youtube.com/watch?v=f1g9GenfTr8&t=736)]
I have these problems too. We need to support CPU and then HCQ2 CPU. We're talking about libclang, right?

##### **Qazalin** [[00:12:32](https://www.youtube.com/watch?v=f1g9GenfTr8&t=752)]
Exactly. You don't want to recompile those helpers every single time.

##### **Geohot** [[00:12:37](https://www.youtube.com/watch?v=f1g9GenfTr8&t=757)]
That's a difference.

##### **Nimlgen** [[00:12:45](https://www.youtube.com/watch?v=f1g9GenfTr8&t=765)]
The linearizer for such programs...

##### **Geohot** [[00:12:49](https://www.youtube.com/watch?v=f1g9GenfTr8&t=769)]
You said the linearizer is slow for HCQ2?

##### **Qazalin** [[00:12:57](https://www.youtube.com/watch?v=f1g9GenfTr8&t=777)]
HCQ2 doesn't even inline the functions. It has a function pointer and calls that pointer, so you effectively link the program with external calls.

##### **Nimlgen** [[00:13:13](https://www.youtube.com/watch?v=f1g9GenfTr8&t=793)]
For USB, for example, if you have a lot of functions...

##### **Qazalin** [[00:13:21](https://www.youtube.com/watch?v=f1g9GenfTr8&t=801)]
It's really slow because it has to recompile the whole thing every time. It doesn't have a way to compile just that part.

##### **Geohot** [[00:13:29](https://www.youtube.com/watch?v=f1g9GenfTr8&t=809)]
I see what you mean. We can play with that. You want these compiled separately. I also see that these could become threads.

##### **Qazalin** [[00:13:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=818)]
Of course. I disabled optimizations because I'm working on getting correctness right, but Clang can do that.

##### **Geohot** [[00:13:48](https://www.youtube.com/watch?v=f1g9GenfTr8&t=828)]
That's transpiling, right? We've lifted the loops; it's transpiling.

##### **Qazalin** [[00:13:52](https://www.youtube.com/watch?v=f1g9GenfTr8&t=832)]
Transpiling is very nice.

##### **Chrism** [[00:13:54](https://www.youtube.com/watch?v=f1g9GenfTr8&t=834)]
The Clang JIT stuff is doable if we add autogen support for it. The reason we don't is that, if you want people to use the libclang JIT API, you need to load the C++ library.

##### **Geohot** [[00:14:14](https://www.youtube.com/watch?v=f1g9GenfTr8&t=854)]
Why would that be?

##### **Qazalin** [[00:14:16](https://www.youtube.com/watch?v=f1g9GenfTr8&t=856)]
I don't think I load C++ here.

##### **Geohot** [[00:14:18](https://www.youtube.com/watch?v=f1g9GenfTr8&t=858)]
I didn't even know there was a libclang JIT API.

##### **Qazalin** [[00:14:24](https://www.youtube.com/watch?v=f1g9GenfTr8&t=864)]
There is one. There's one for LLVM.

##### **Geohot** [[00:14:26](https://www.youtube.com/watch?v=f1g9GenfTr8&t=866)]
What was that other thing we used to use? This would get rid of ELF and stuff.

##### **Qazalin** [[00:14:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=878)]
It does, actually, I think, with the Clang JIT.

##### **Geohot** [[00:14:42](https://www.youtube.com/watch?v=f1g9GenfTr8&t=882)]
We can talk about this.

##### **Chrism** [[00:14:44](https://www.youtube.com/watch?v=f1g9GenfTr8&t=884)]
I'll read that.

##### **Geohot** [[00:14:46](https://www.youtube.com/watch?v=f1g9GenfTr8&t=886)]
We can decide what we want to do here.

##### **Qazalin** [[00:14:52](https://www.youtube.com/watch?v=f1g9GenfTr8&t=892)]
It's not a hand-rolled Python JIT. I just used whatever Clang provides. You'll see the function arguments are SGPR, VGPR, the address, and the VMAP.

##### **Geohot** [[00:15:11](https://www.youtube.com/watch?v=f1g9GenfTr8&t=911)]
That needs to be fixed.

##### **Qazalin** [[00:15:12](https://www.youtube.com/watch?v=f1g9GenfTr8&t=912)]
I know, but it's the simplest way. I'm going to clean up the algorithm that does the lifting, then do the ranges.

##### **Geohot** [[00:15:31](https://www.youtube.com/watch?v=f1g9GenfTr8&t=931)]
Why does that one stay a BACKEDGE? That's a BACKEDGE, right? Can you lift it, make it a RANGE?

##### **Qazalin** [[00:15:37](https://www.youtube.com/watch?v=f1g9GenfTr8&t=937)]
We don't have anything to do that.

##### **Geohot** [[00:15:42](https://www.youtube.com/watch?v=f1g9GenfTr8&t=942)]
I think codegen can do it.

##### **Qazalin** [[00:15:45](https://www.youtube.com/watch?v=f1g9GenfTr8&t=945)]
Got it. It's a generic codegen thing: if you had a BACKEDGE and a loop in your custom kernel, you could lift it to a RANGE.

##### **Geohot** [[00:15:54](https://www.youtube.com/watch?v=f1g9GenfTr8&t=954)]
Cool. Good.

##### **Chenyu** [[00:16:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=964)]
Okay, next is my stuff. We discussed replacing PAD with STACK: stack a bunch of zeros, then reshape and shrink. It's annoying with the KV cache, where you pad a symbolic amount, because STACK requires the same amount. I think that's the most annoying case.

##### **Chenyu** [[00:16:33](https://www.youtube.com/watch?v=f1g9GenfTr8&t=993)]
I started looking into the current STACK code, trying to simplify it, and broke something. That made me realize there are more opportunities for symbolic optimization around STACK. I already found one in the LT folding that makes the code simpler. Previously, for WHERE or IMAGE, we did a lot of analysis by splitting the whole line into two parts. We have simplex analysis on the region, and outside that region it can be zero, things like that.

##### **Chenyu** [[00:17:15](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1035)]
The interesting part is that STACK gives you more than a simplex. Sometimes it just takes a slice, but there are other properties we currently don't model. For example, if you bitwise-AND an index with six, that restricts the possible values and gives you properties modulo two or four. It can pick out individual values that we didn't previously model. STACK gives us flexibility, and modeling that is interesting.

##### **Chenyu** [[00:18:00](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1080)]
LLVM has a whole pass around knowing which bits are guaranteed to be zero, which is a more generic version of the simplex analysis we were doing. I'm trying to see what parts we can bring into our model. I think it's a good idea to do it within the current framework without adding all the complexity.

##### **Geohot** [[00:18:26](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1106)]
At what level do you want to do it? Before STACK is lowered, or after?

##### **Chenyu** [[00:18:32](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1112)]
You lower it into WHERE, right?

##### **Geohot** [[00:18:36](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1116)]
Yeah.

##### **Chenyu** [[00:18:37](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1117)]
The thing that broke yesterday was part of rangeify. After lowering to WHERE, it should be generic with the current WHERE; there's nothing special about STACK anymore. There are a lot of ways to say the same thing. If x is an integer less than seven and greater than five, you can solve that: x must be six, so replace it with six. We don't currently have a good language to describe that, because previously we only had less-than, and it was always less-than.

##### **Geohot** [[00:19:19](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1159)]
Yeah.

##### **Chenyu** [[00:19:23](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1163)]
That's pretty much it. I also want to find other minor STACK and symbolic bugs, and do more cleanups after removing pyrender. A lot of rendering stuff is only used by symbolic, so I'm cleaning that up too.

##### **Geohot** [[00:19:46](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1186)]
Do we like STACK?

##### **Chenyu** [[00:19:49](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1189)]
I think STACK is pretty nice.

##### **Geohot** [[00:19:52](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1192)]
It's the simplest form of all of this. You need some combinator movement op, some way to take two buffers and put them together. A STACK construction is a lot nicer than PAD/ADD.

##### **Chenyu** [[00:20:13](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1213)]
It's just not clear whether STACK or CAT is better.

##### **Geohot** [[00:20:18](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1218)]
Oh no, CAT is...

##### **Chenyu** [[00:20:21](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1221)]
CAT is scary. STACK is scary compared to PAD too, because it's more flexible now.

##### **Geohot** [[00:20:30](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1230)]
Yeah, CAT is even scarier.

##### **Chenyu** [[00:20:33](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1233)]
There seems to be a balance: where do we stop, between how good our symbolic engine is and how simply we can represent things?

##### **Geohot** [[00:20:43](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1243)]
Yeah, I don't think we want that.

##### **Chenyu** [[00:20:46](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1246)]
Motivated by multi-device and other thread-like things, STACK probably makes more sense. We'll stick with it and see how other things work.

##### **Geohot** [[00:21:01](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1261)]
I like STACK a lot better than PAD/ADD constructions.

##### **Chenyu** [[00:21:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1264)]
Of course.

##### **Geohot** [[00:21:05](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1265)]
The problem with CAT: we could do it, and it would stitch the first dimension. We can discuss this later.

##### **Chenyu** [[00:21:16](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1276)]
We don't yet have a solution for a lot of multi-device stuff. It motivates looking at the primitives we already use.

##### **Geohot** [[00:21:28](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1288)]
The other problem with CAT is that STACK works beautifully for CONSTs. STACK on CONST is VCONST. CAT on CONST can't really do that. What axis are you concatenating along? That's why I went with STACK.

##### **Chenyu** [[00:21:48](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1308)]
We'll stick with this. Every time we find something LLVM is doing that we're not, it's a good idea to think about it. That's pretty much it.

##### **Chenyu** [[00:22:03](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1323)]
Okay, with that, let's move on to HCQ2.

##### **Nimlgen** [[00:22:13](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1333)]
A bunch of cleanups. We now have proper error handling and timeouts in HCQ2. I also have fast disk reads now, about 23 GB/s on the RAID.

##### **Geohot** [[00:22:27](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1347)]
Wait, 22 on which RAID?

##### **Nimlgen** [[00:22:31](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1351)]
On G3.

##### **Geohot** [[00:22:33](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1353)]
Okay. I was going to say, 22 on a PCIe 4 machine is great. On a PCIe 5 machine, that's okay.

##### **Nimlgen** [[00:22:42](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1362)]
We also have the HIP backend now. It just reuses CUDA. I'll still do a bunch of cleanups.

##### **Geohot** [[00:23:01](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1381)]
Wow, HIP's so small. HIPify. You just transform the IR. That's pretty good. It's a pattern-matcher transformation from CUDA to HIP. You could do the other way around too. All respect to him.

##### **Geohot** [[00:23:48](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1428)]
This brings up an interesting question: do we want to move CALL source zero to the arg? Do you guys feel strongly about that? I'd like to remove enter_calls, though it's still kind of nice on toposort.

##### **Qazalin** [[00:24:30](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1470)]
It's off by default.

##### **Geohot** [[00:24:31](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1471)]
We shouldn't allow it in graph_rewrite. In toposort, I use it in a few places in studentgrad. It's nice because studentgrad has a requirement that tests be under a hundred UOps, and I obviously want to enter CALLs.

##### **Nimlgen** [[00:24:55](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1495)]
I'm not sure about enter_calls. What exactly are you talking about?

##### **Geohot** [[00:25:02](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1502)]
On graph_rewrite. You're using it here, right?

##### **Nimlgen** [[00:25:10](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1510)]
We can discuss how HCQ2 works later, but we just need to rewrite the body.

##### **Geohot** [[00:25:19](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1519)]
There's another way to write it: have a pattern matcher on a CALL that triggers another graph_rewrite. That might be the canonical way. You can trigger the same pattern matcher.

##### **Nimlgen** [[00:25:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1538)]
It will have more graph_rewrites.

##### **Geohot** [[00:25:40](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1540)]
Yeah, it creates more graph_rewrites. I don't know, I'm kind of liking enter_calls. I see what this does and why you want it. If we're going to keep enter_calls as an option, CALL shouldn't move to arg. I don't know how much slower src_without_body makes it. It's a premature optimization. We want to decide semantically whether we want source zero or arg.

##### **Qazalin** [[00:26:17](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1577)]
By its nature, it's a little recursive.

##### **Nimlgen** [[00:26:27](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1587)]
It's not really slow. It doesn't look good, but I'm sure it's not slow.

##### **Geohot** [[00:26:35](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1595)]
You're creating a new graph_rewrite for each...

##### **Qazalin** [[00:26:41](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1601)]
I remember why I wanted this.

##### **Nimlgen** [[00:26:52](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1612)]
It's not the whole graph_rewrite; it just iterates over the important part.

##### **Qazalin** [[00:26:58](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1618)]
Otherwise it will keep rewriting it.

##### **Geohot** [[00:27:02](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1622)]
Wait, what?

##### **Qazalin** [[00:27:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1624)]
It won't rewrite it in graph_rewrite as a CALL, but it will rewrite it in the CALL method. It's like the method cache, but for CALL.

##### **Geohot** [[00:27:17](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1637)]
That doesn't make a difference between source and arg. We have the same problem.

##### **Qazalin** [[00:27:21](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1641)]
It makes a difference if you have the recursive pattern matcher.

##### **Geohot** [[00:27:32](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1652)]
With the recursive pattern matcher, you can cache it, but you don't cache it by default.

##### **Qazalin** [[00:27:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1658)]
We don't cache it by default.

##### **Geohot** [[00:27:44](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1664)]
enter_calls is always faster. It caches everything in a single cache.

##### **Qazalin** [[00:27:49](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1669)]
It won't persist globally. Method cache.

##### **Geohot** [[00:27:54](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1674)]
You have to write the method cache. That's not an argument. The CALL cache can become basically global, but this doesn't affect enter_calls. We should go through HCQ2, figure out where it uses enter_calls, and think about whether the other construction is better. We could even keep enter_calls=True and just add a pattern matcher at the end that triggers the same pattern matcher on the body. We wouldn't have to change the API.

##### **Chrism** [[00:28:44](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1724)]
I think it's nice to force you to write a little extra stuff.

##### **Geohot** [[00:29:03](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1743)]
That's not the question. It's not whether you can write it; it's how easy we want to make it for programmers. ctx is too short a name. It should be called context_graph_do_not_use_this. At the very least, use the full word context rather than ctx.

##### **Chenyu** [[00:29:33](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1773)]
One thing to add: HCQ2 used to have an off-by-one on the timeline or some error, and I saw you fixed it. There was a memoryview-check bug; you fixed that?

##### **Nimlgen** [[00:29:53](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1793)]
Probably, yes.

##### **Chenyu** [[00:29:55](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1795)]
There's another place with a similar pattern, but now it reads differently, and I'm not sure it's right.

##### **Nimlgen** [[00:30:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1804)]
Sure.

##### **Chenyu** [[00:30:05](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1805)]
I'll post it somewhere after this. I tried to fix it and wasn't sure of the solution, because there are two sets of very similar code that now read differently.

##### **Chenyu** [[00:30:17](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1817)]
Okay, anything else?

##### **Nimlgen** [[00:30:19](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1819)]
No.

##### **Chenyu** [[00:30:20](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1820)]
We'll discuss HCQ2 and CPU codegen later. Okay, next is CI.

##### **Chrism** [[00:30:31](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1831)]
CI, at least for collaborators, is self-hosted now. I don't know if anyone has experienced issues. I saw that intermittent issue with logs not showing up that one time.

##### **Nimlgen** [[00:30:46](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1846)]
What was the change?

##### **Chrism** [[00:30:49](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1849)]
We're self-hosted. CI is running on our machines in the data center.

##### **Geohot** [[00:30:54](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1854)]
Yeah.

##### **Chrism** [[00:30:57](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1857)]
It's about the same speed.

##### **Geohot** [[00:30:59](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1859)]
But it's cheaper.

##### **Chrism** [[00:31:00](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1860)]
That's true. One thing I've noticed is that queue times are a little longer. Namespace's average is about twelve seconds, and ours is closer to twenty. This needs to be fixed upstream. It's partially fixed now, and I talked to the maintainer; he's going to fully fix it. He says he's about to cut a release, so I won't have to pin a branch anymore. I'm going to wait for that release.

##### **Geohot** [[00:31:39](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1899)]
We get to cancel Namespace?

##### **Chrism** [[00:31:41](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1901)]
Yeah.

##### **Geohot** [[00:31:42](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1902)]
Boom. Love saving money.

##### **Chrism** [[00:31:46](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1906)]
That's the big news. If there are any issues, let me know. Now we have to be especially careful deploying to machines, because...

##### **Chenyu** [[00:31:57](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1917)]
Say more.

##### **Chrism** [[00:31:59](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1919)]
There's more stuff to affect. Previously, if you botched a deploy, the impact was relatively minimal. Now it's somewhat larger.

##### **Chenyu** [[00:32:10](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1930)]
What deploy? Who's doing these deployments?

##### **Chrism** [[00:32:14](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1934)]
The pyinfra deploy.

##### **Chenyu** [[00:32:16](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1936)]
Oh, the pyinfra deploy. Okay, you always need to be careful with that.

##### **Chrism** [[00:32:19](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1939)]
Sure, but the blast radius...

##### **Chenyu** [[00:32:23](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1943)]
In the way I use GitHub, is there any way I could bring it down that I need to be careful about?

##### **Chrism** [[00:32:30](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1950)]
No, unless you're running update_benchmark every ten seconds.

##### **Geohot** [[00:32:36](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1956)]
We need to be more robust. This shouldn't be a problem. If you're messing with the infrastructure, that's different.

##### **Chrism** [[00:32:45](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1965)]
I have a PR open to start self-hosting update_benchmark as well.

##### **Geohot** [[00:32:53](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1973)]
We use $80,000 worth of computers to save $2,000 in cloud bills. Yeah!

##### **Chrism** [[00:33:03](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1983)]
A problem with update_benchmark is that sometimes when you cancel a run, it breaks everything. That should go away once everything is in VMs.

##### **Geohot** [[00:33:19](https://www.youtube.com/watch?v=f1g9GenfTr8&t=1999)]
I think we'll upgrade the GPUs in those machines too.

##### **Chrism** [[00:33:25](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2005)]
That's why I started with the PCI driver tests. For benchmarks, it doesn't...

##### **Geohot** [[00:33:34](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2014)]
The cheap ones are fine. I think we'll put 9070s and maybe 5070s in there, something we can fit.

##### **Chrism** [[00:33:43](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2023)]
For the LLM tests, don't we have specific code to make RDNA3 performance good?

##### **Geohot** [[00:33:54](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2034)]
Yeah, but we have so many other RDNA3 boxes.

##### **Chrism** [[00:33:56](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2036)]
So we turn those into VM hosts too?

##### **Geohot** [[00:34:00](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2040)]
Yeah. Those are going to be our machines; we'll retire the G machines.

##### **Chrism** [[00:34:08](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2048)]
Sounds good.

##### **Chenyu** [[00:34:09](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2049)]
For benchmarks, be careful about machine variation. It's annoying to get a slower machine or a faster server.

##### **Chrism** [[00:34:19](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2059)]
I was going to change runs-on to just runs-on: 3080 or runs-on: 9060.

##### **Chenyu** [[00:34:25](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2065)]
Just check the end-to-end time when someone opens something new in CI or updates the benchmark. Let it finish, to make sure...

##### **Chrism** [[00:34:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2078)]
The total duration, you mean?

##### **Chenyu** [[00:34:40](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2080)]
Yeah.

##### **Geohot** [[00:34:41](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2081)]
Does anyone want to buy a 4090 box? Lightly used. They work pretty well; they're great. Anyway.

##### **Chrism** [[00:34:53](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2093)]
You can reserve a VM for yourself, your agent, or a student in the future. That'll be nice. We need an interface for that.

##### **Geohot** [[00:35:06](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2106)]
We'll get some tinybox talls with tons of 3080s for the students. Students will do development on 3080s.

##### **Chrism** [[00:35:17](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2117)]
I have to build a little management interface.

##### **Geohot** [[00:35:20](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2120)]
Everybody here with tinybox access will move to VM access. It could even share the VMs with CI. Should be pretty good.

##### **Chrism** [[00:35:34](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2134)]
It should be good. You can insert the NVIDIA kernel module if you need it without worrying about breaking other people's stuff. I need to SSH into these and have an agent try to break the GPU, and see if it can.

##### **Geohot** [[00:35:53](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2153)]
Maybe we want to move the 4090 machines too. Can we request VMs with multiple GPUs?

##### **Chrism** [[00:36:00](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2160)]
I have to add that too. We'll see how this works. Right now I'm thinking we'll have preconfigured options: you can get a machine with two 3090s, for example, or another configuration from a list of acceptable SKUs.

##### **Geohot** [[00:36:17](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2177)]
Exactly.

##### **Chrism** [[00:36:18](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2178)]
Rather than arbitrary combinations, like a 9070 and this and that.

##### **Geohot** [[00:36:24](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2184)]
No, it won't be arbitrary configurations. You can run on two 3080s.

##### **Chrism** [[00:36:30](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2190)]
We have to do that anyway, because some benchmark tests run on them.

##### **Geohot** [[00:36:34](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2194)]
But two 3080s shouldn't be reserved as a fixed pair. They can be booked as one 3080 too. As long as you do that, that's fine. I don't want reserved SKUs taking a machine with ten 3080s and setting aside two fixed pairs of 3080s, for example.

##### **Chrism** [[00:36:54](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2214)]
That was the question: is this something we want to do? It requires an additional level of complexity. Right now, the way I modeled this was that the VMs were totally isolated. Especially if your VMs are on the same machine versus different machines, and you want them to be able to network together.

##### **Geohot** [[00:37:20](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2240)]
You want multi-machine? Do you think it's important? Does it work on master?

##### **Chrism** [[00:37:25](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2245)]
You can do it, but I guess it doesn't exercise the network card. You're not getting a real network.

##### **Geohot** [[00:37:36](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2256)]
Maybe not for now, not for the course.

##### **Chrism** [[00:37:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2258)]
You'd have to include the network card in the VM.

##### **Geohot** [[00:37:49](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2269)]
Maybe we can do this.

##### **Chrism** [[00:37:51](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2271)]
With network cards and stuff...

##### **Geohot** [[00:37:53](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2273)]
What do you mean? It's just one network card per machine. That solves what happens if you get them on the same machine.

##### **Chrism** [[00:38:00](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2280)]
Right, but then you have to reserve two.

##### **Geohot** [[00:38:05](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2285)]
Is it possible? You have to reserve two.

##### **Chrism** [[00:38:10](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2290)]
It seems to increase the complexity a lot.

##### **Chenyu** [[00:38:14](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2294)]
If it's not a natural extension of what you're doing now, it's probably not worth it.

##### **Geohot** [[00:38:19](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2299)]
I think we'll end up with three red boxes in the VM setup. Or we keep the 4090 boxes and include them too.

##### **Chrism** [[00:38:32](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2312)]
It depends on how valuable we think it is to have those tests.

##### **Geohot** [[00:38:35](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2315)]
The whole thing could be three red boxes, three 4090 boxes, and three of the current boxes.

##### **Chrism** [[00:38:44](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2324)]
When we add more machines, we can reevaluate.

##### **Chenyu** [[00:38:51](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2331)]
Unless someone offers a premium for those boxes.

##### **Geohot** [[00:38:55](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2335)]
Let me put them up on the store if people want to buy them. Anyway, let's move on with the meeting. Anything else?

##### **Chrism** [[00:39:05](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2345)]
No, that's it.

##### **Chenyu** [[00:39:07](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2347)]
That's the regular items. I didn't include B1tg because I didn't know if he'd attend. I have LLMs, RDNA, and Comma. Is Comma happy?

##### **Chrism** [[00:39:25](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2365)]
Right now they're on their own fork of tinygrad.

##### **Geohot** [[00:39:31](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2371)]
That doesn't seem happy.

##### **Chrism** [[00:39:32](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2372)]
There's one commit, and Daniel has a PR open. We merged one of the things; the other is the one you just commented on.

##### **Nimlgen** [[00:39:44](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2384)]
Why do they want the other one?

##### **Chrism** [[00:39:47](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2387)]
I don't know either. I'll ask whether it's actually important.

##### **Geohot** [[00:39:52](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2392)]
We can have Chestnuts on the test machines, though?

##### **Chrism** [[00:39:54](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2394)]
I think so. This test runs on a Mac. I don't know about Mac VMs, but we can do Chestnuts. Are there USB-C ports on the tinyboxes?

##### **Geohot** [[00:40:08](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2408)]
USB 3 and C? What do you mean by C? C is a hole.

##### **Chrism** [[00:40:13](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2413)]
Sure.

##### **Geohot** [[00:40:14](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2414)]
What is the PR?

##### **Chrism** [[00:40:17](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2417)]
It's old.

##### **Geohot** [[00:40:33](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2433)]
We can try to reproduce it here. We have a Chestnut.

##### **Chrism** [[00:40:37](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2437)]
My guess is that he added it. I'm just throwing an LLM at this, so I'm not sure.

##### **Geohot** [[00:40:50](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2450)]
[Unclear remark about the comma four and Chestnut.] Can we get some Comma hardware here?

##### **Chrism** [[00:41:03](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2463)]
I should have brought some.

##### **Chenyu** [[00:41:06](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2466)]
We have comma 3Xs here. I think it's the same.

##### **Geohot** [[00:41:10](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2470)]
Pretty much.

##### **Chenyu** [[00:41:13](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2473)]
We have comma 3Xs. Let's discourage Comma from being on a fork.

##### **Chrism** [[00:41:19](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2479)]
They needed this slot.

##### **Geohot** [[00:41:23](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2483)]
Let's discourage that. Every time they open a PR, they're like, 'I don't maintain this code, so I'll just slop it all up.'

##### **Geohot** [[00:41:39](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2499)]
The other thing I want to talk about is moving tinycorp to self-hosting our LLMs. The first thing we can do is get GLM-5.3 off SGLang and move to tinygrad. Wozeparrot, how do you feel about that project?

##### **Wozeparrot** [[00:42:07](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2527)]
I was just going to say I probably want to take that on.

##### **Geohot** [[00:42:11](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2531)]
Cool. We want to add GLM-5.3 and get on this AgentX thing. That's the new thing AMD is interested in if we get a new contract. There's also a very interesting TileRT for GLM-5.3. TileRT is from the TileLang people. The kernels are closed source, but nothing's closed source anymore, so you can look at them. They have really high interactivity.

##### **Geohot** [[00:42:58](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2578)]
We basically want tinyamd2. We can kick Comma off tinyamd2 if they're still using it; they can buy their own AMD machine. We want to see what it'll take to get us on there. Let's take notes now: tinyamd2, GLM-5.3, get it on InferenceX by SemiAnalysis.

##### **Geohot** [[00:43:27](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2607)]
This would be the new AMD contract. We only have so much social capital with AMD. More interesting than a new contract is pricing for the secret project. But if we show them we can get the 350s or the 300s on this, they'll send us 450s.

##### **Wozeparrot** [[00:44:01](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2641)]
I see.

##### **Geohot** [[00:44:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2644)]
I think we should focus on 300s more than 350s, for the...

##### **Chenyu** [[00:44:13](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2653)]
Obvious reason.

##### **Geohot** [[00:44:15](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2655)]
For the obvious reason that we own a bunch of 300s, and they mostly kind of work. We're going to have a lot of 300s. We all know what that's about.

##### **Chenyu** [[00:44:34](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2674)]
I don't believe there's other bounty progress.

##### **Geohot** [[00:44:37](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2677)]
Which bounty? Oh, I've got to merge that. He eventually came up with something: buffers and args in any order. It's stale again. Is it good?

##### **Geohot** [[00:44:51](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2691)]
Yeah, I locked the bounty for it.

##### **Chrism** [[00:44:56](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2696)]
What about Ocelot? This is annoying. In the CI VMs, I ship two versions of CUDA now.

##### **Geohot** [[00:45:03](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2703)]
You what?

##### **Chrism** [[00:45:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2704)]
I ship two versions of CUDA.

##### **Geohot** [[00:45:05](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2705)]
What do you mean?

##### **Chrism** [[00:45:06](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2706)]
CUDA 11 and CUDA 12.

##### **Geohot** [[00:45:08](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2708)]
Do you want to get it merged?

##### **Chrism** [[00:45:11](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2711)]
Yeah. I don't want to read C++.

##### **Geohot** [[00:45:14](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2714)]
I know. There's also the Qualcomm emulator to merge. We have bounties to merge; it's just finding time to read the AI slop.

##### **Geohot** [[00:45:31](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2731)]
For recruiting, we have the Carnegie Mellon class, hopefully.

##### **Geohot** [[00:45:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2738)]
Not just the students, but yeah...

##### **Chenyu** [[00:45:42](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2742)]
It's just 1,100 lines in extra?

##### **Geohot** [[00:45:47](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2747)]
Why not? With the Qualcomm emulator, at least we can test the real model. That's what I told him to add. If he added that and made it work, I think we'll... Okay. We should each take one and get it merged. Who wants the Qualcomm emulator? Qazalin, I'm looking at you.

##### **Qazalin** [[00:46:17](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2777)]
The Qualcomm emulator?

##### **Geohot** [[00:46:23](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2783)]
It's like the AMD emulator. You know the best about emulators. I'll take buffers and args in any input order. We'll get these bounties merged and paid out.

##### **Nimlgen** [[00:46:38](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2798)]
Raine will be here?

##### **Geohot** [[00:46:42](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2802)]
Yeah. Not right now.

##### **Chenyu** [[00:46:45](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2805)]
Great, so we can discuss more about RDNA soon. That's pretty much it.

##### **Geohot** [[00:46:51](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2811)]
For LLMs, we're going to need a multithreaded server. I have a PR for that, which is mostly fine. My biggest problem with it is that it makes the log lines not pretty. More important than the multithreaded server, though, is supporting decode with variable batch sizes. Is there ever an advantage to doing batch-size-two prefill?

##### **Chenyu** [[00:47:29](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2849)]
Anyone know?

##### **Wozeparrot** [[00:47:31](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2851)]
For multi-user?

##### **Geohot** [[00:47:32](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2852)]
For multi-user, yes. When you do prefill, do you do it for multiple users?

##### **Wozeparrot** [[00:47:41](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2861)]
My understanding is that you want to batch the prefill.

##### **Geohot** [[00:47:45](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2865)]
Really? If you're already pegging the FLOPS of the GPU, how does that help?

##### **Wozeparrot** [[00:47:58](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2878)]
Maybe not. I think it's an MoE thing, depending on where you're routing.

##### **Geohot** [[00:48:07](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2887)]
We have to batch decode for multiple users; that's obvious. I don't know about batching prefill, or how much it'd matter if we're really using all the GPU's FLOPS. With a little work we can support multiple users. If we support variable-batch decodes, we can also support speculative decoding.

##### **Qazalin** [[00:48:30](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2910)]
[Unclear brief aside.]

##### **Geohot** [[00:48:39](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2919)]
I don't know if we need a radix cache, all that fancy, heavy KV-cache radix stuff.

##### **Chenyu** [[00:48:48](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2928)]
We should probably have some reasonable cache expiration.

##### **Geohot** [[00:48:58](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2938)]
If I submit the same thing twice...

##### **Nimlgen** [[00:49:00](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2940)]
Least recently used.

##### **Chenyu** [[00:49:02](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2942)]
How recent is recent?

##### **Geohot** [[00:49:04](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2944)]
I don't know what SGLang and vLLM's cache policies are or how complex they are.

##### **Wozeparrot** [[00:49:11](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2951)]
It can get very, very complex. I think vLLM has about ten cache-eviction options.

##### **Nimlgen** [[00:49:22](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2962)]
Is the default one complex?

##### **Wozeparrot** [[00:49:27](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2967)]
No. I think most of them just use LRU anyway.

##### **Geohot** [[00:49:32](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2972)]
LRU seems more than enough. Again, we want to move this organization off SGLang and onto tinygrad. Great, sounds good.

##### **Chenyu** [[00:49:43](https://www.youtube.com/watch?v=f1g9GenfTr8&t=2983)]
I think that's it for this meeting. Anything else? No? Okay, that's it. Thank you, everyone. See you next week. Bye-bye.
