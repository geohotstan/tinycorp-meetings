# 2025-11-17 Meeting

### Meeting Agenda

**Time:** 9am Monday San Diego time
- company update, new intern
- openpilot regression, conv regression, hevc decode
- LLaMA mem usage, outerworld range, fp8?
- SQTT
- tinykitten flash attention
- other bounties

### Audio

[Youtube Link](https://www.youtube.com/watch?v=cLnu8McQRlw)

### Highlights

- **[Company Updates and RedV2](#chenyu-000028)**: RedV2 has launched, with Geohot offering SSH access to machines for anyone reputable willing to run LLM benchmarks.
- **[EGraphs and Rewrite Rules](#qazalin-000254)**: Discussion on potentially using EGraphs to solve rewrite rule ordering and indexing issues, with plans to implement an EGraph saturation engine if current fixes fail.
- **[HEVC Decode for Comma](#nimlgen-000617)**: Comma expressed interest in edge event decode; the team plans to test HEVC throughput and optimize resizing kernels by flattening 2D indexes.
- **[LLaMA Training Strategy](#qazalin-000939)**: The roadmap for LLaMA involves three parallel tracks: getting 8B training to work, implementing custom Flash Attention kernels to reduce memory usage, and differentiating outer world loops.
- **[Differentiable Scan Operator](#geohot-001105)**: Geohot is working on a differentiable scan operator to avoid range-ifying massive graphs, aiming for completion by the end of the week.
- **[End of Year Goals](#nimlgen-001450)**: Objectives set for the end of the year include working custom Flash Attention/GEMM, 8B training hitting MLPerf targets, and sub-20 second Python time for LLaMA 405B.
- **[SQTT Timeline Visualization](#qazalin-001614)**: Qazalin merged the SQTT timeline which visualizes wave dispatch cycles on a separate graph, utilizing Rockm profile traces.
- **[Tiny Kittens and MI350](#qazalin-002555)**: Updates on Tiny Kittens support for MI350, focusing on shared memory swizzling to handle bank conflicts without resorting to raw assembly.
- **[Issue Backlog and Bounties](#chenyu-003249)**: The team plans to tackle the 127 open issues now that major refactors are done; discussion on banning users who copy-paste misunderstood AI code for bounties.
- **[AMD Timing and Synchronization](#geohot-004401)**: Geohot fixed a timing bug on RDNA4 related to `release_mem` semantics, discovered by cross-referencing Mesa driver details.

### Transcript
##### **Geohot** [[00:00:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=0)]
Okay, let's get started.

##### **Qazalin** [[00:00:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=3)]
Start with company update.

##### **Chenyu** [[00:00:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=7)]
Yeah, right.

##### **Nimlgen** [[00:00:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=10)]
Chris,

##### **Qazalin** [[00:00:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=11)]
I mean, I've been talking on these meetings before, but

##### **Geohot** [[00:00:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=13)]
yeah, I'm doing a work trial this week.

##### **Geohot** [[00:00:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=18)]
Yeah. Cool.

##### **Geohot** [[00:00:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=26)]
Cool.

##### **Qazalin** [[00:00:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=27)]
Great.

##### **Chenyu** [[00:00:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=28)]
So we launched

##### **Nimlgen** [[00:00:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=31)]
RedV2?

##### **Qazalin** [[00:00:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=35)]
Yeah, we launched RedV2.

##### **Geohot** [[00:00:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=36)]
We haven't sold one yet.

##### **Geohot** [[00:00:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=39)]
So we'll see if anyone

##### **Geohot** [[00:00:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=41)]
buys them. We made like four of them.

##### **Qazalin** [[00:00:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=43)]
I have one in my office. It's pretty nice.

##### **Chenyu** [[00:00:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=47)]
Oh, if you click on the link,

##### **Nimlgen** [[00:00:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=49)]
it goes to a tweet.

##### **Qazalin** [[00:00:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=51)]
If you click on that top link, yeah,

##### **Geohot** [[00:00:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=52)]
it goes to just the Twitter thread where I did all the benchmarks and stuff.

##### **Geohot** [[00:01:02](https://www.youtube.com/watch?v=cLnu8McQRlw&t=62)]
If anyone out there has like a reputation

##### **Geohot** [[00:01:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=65)]
for doing this and wants

##### **Qazalin** [[00:01:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=66)]
to do LLM benchmarks, I'll give you

##### **Chenyu** [[00:01:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=69)]
SSH to the machines.

##### **Nimlgen** [[00:01:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=77)]
Dylan never reached out about that.

##### **Qazalin** [[00:01:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=80)]
No, no, no.

##### **Geohot** [[00:01:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=81)]
They got a lot of stuff to tell.

##### **Geohot** [[00:01:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=89)]
Yeah, so two main things

##### **Geohot** [[00:01:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=91)]
for the meeting. One is about

##### **Qazalin** [[00:01:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=93)]
Karma, one is about the

##### **Chenyu** [[00:01:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=95)]
Karma

##### **Nimlgen** [[00:01:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=97)]
MLperf thing.

##### **Qazalin** [[00:01:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=99)]
We can quickly go through the Karma stuff

##### **Geohot** [[00:01:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=101)]
first.

##### **Geohot** [[00:01:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=105)]
Karma after

##### **Geohot** [[00:01:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=106)]
the

##### **Qazalin** [[00:01:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=111)]
first

##### **Chenyu** [[00:01:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=112)]
update, we had a lot of

##### **Nimlgen** [[00:02:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=120)]
issues with the

##### **Qazalin** [[00:02:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=121)]
LLM

##### **Geohot** [[00:02:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=121)]
LLM

##### **Geohot** [[00:02:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=121)]
and the

##### **Geohot** [[00:02:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=121)]
and the

##### **Qazalin** [[00:02:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=121)]
LLM

##### **Chenyu** [[00:02:02](https://www.youtube.com/watch?v=cLnu8McQRlw&t=122)]
and the

##### **Nimlgen** [[00:02:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=125)]
LLM

##### **Qazalin** [[00:02:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=125)]
and the

##### **Geohot** [[00:02:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=137)]
LLM

##### **Geohot** [[00:02:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=137)]
LLM.

##### **Geohot** [[00:02:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=148)]
So, we have to

##### **Qazalin** [[00:02:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=151)]
build that.

##### **Chenyu** [[00:02:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=151)]
build that in the

##### **Nimlgen** [[00:02:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=153)]
LLM

##### **Qazalin** [[00:02:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=155)]
LLM

##### **Geohot** [[00:02:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=155)]
LLM

##### **Geohot** [[00:02:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=155)]
LLM

##### **Geohot** [[00:02:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=156)]
LLM

##### **Qazalin** [[00:02:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=156)]
LLM

##### **Chenyu** [[00:02:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=156)]
LLM

##### **Nimlgen** [[00:02:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=157)]
LLM

##### **Qazalin** [[00:02:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=160)]
LLM

##### **Geohot** [[00:02:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=168)]
EGraphs don't actually need..

##### **Geohot** [[00:02:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=170)]
I thought they needed a different kind of rewrite rule.

##### **Geohot** [[00:02:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=172)]
They don't.

##### **Qazalin** [[00:02:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=174)]
The only thing EGraphs need is

##### **Chenyu** [[00:02:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=177)]
a promise that any rewrite rule that does trigger

##### **Nimlgen** [[00:03:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=180)]
is invertible.

##### **Qazalin** [[00:03:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=181)]
So if you've substituted node A for node B,

##### **Geohot** [[00:03:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=184)]
you could also substitute node B back for node A.

##### **Geohot** [[00:03:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=186)]
That's always safe.

##### **Geohot** [[00:03:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=192)]
Which is like true for all symbolic rules.

##### **Qazalin** [[00:03:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=195)]
So we could actually probably write like a 100-line..

##### **Chenyu** [[00:03:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=198)]
EGraph saturation engine.

##### **Nimlgen** [[00:03:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=199)]
I don't know.

##### **Qazalin** [[00:03:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=200)]
When you look at the symbolic more,

##### **Geohot** [[00:03:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=201)]
if a lot of the problems just come down to like

##### **Geohot** [[00:03:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=204)]
finicky rule order application stuff,

##### **Geohot** [[00:03:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=208)]
then maybe we consider doing it with EGraphs.

##### **Qazalin** [[00:03:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=210)]
I don't think this one is ordering,

##### **Chenyu** [[00:03:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=212)]
but I would know better after I look more.

##### **Nimlgen** [[00:03:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=214)]
Because I also try to simply

##### **Qazalin** [[00:03:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=217)]
like looking something for the order

##### **Geohot** [[00:03:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=219)]
to see if it happens to make both work.

##### **Geohot** [[00:03:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=222)]
It didn't work.

##### **Geohot** [[00:03:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=224)]
Yeah.

##### **Qazalin** [[00:03:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=224)]
No, I just don't want to waste a lot of time.

##### **Chenyu** [[00:03:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=226)]
Like, oh, we got to get this order

##### **Nimlgen** [[00:03:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=227)]
of these rules exactly right.

##### **Qazalin** [[00:03:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=229)]
So I don't think it's that.

##### **Geohot** [[00:03:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=230)]
I think it's a good opportunity to also see

##### **Geohot** [[00:03:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=232)]
if we can further clean up the indexing a bit.

##### **Geohot** [[00:03:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=236)]
Yeah.

##### **Qazalin** [[00:03:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=237)]
So the other thing too is like,

##### **Chenyu** [[00:03:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=239)]
it does kind of look like indexing is this separate kind of like..

##### **Nimlgen** [[00:04:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=243)]
We use the rewrite engine for a lot of stuff.

##### **Qazalin** [[00:04:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=246)]
I'd be okay with like only enabling an EGraph saturation

##### **Geohot** [[00:04:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=248)]
on the indexing rewrite.

##### **Geohot** [[00:04:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=251)]
And yeah, it'll make the indexing rewrite a little bit slower,

##### **Geohot** [[00:04:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=254)]
but I don't think it's that..

##### **Qazalin** [[00:04:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=256)]
It's very slow.

##### **Chenyu** [[00:04:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=257)]
It's very slow anyway.

##### **Nimlgen** [[00:04:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=258)]
Like most of the rewrites are not indexing.

##### **Qazalin** [[00:04:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=259)]
So even if we get like a 5x speed hit

##### **Geohot** [[00:04:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=261)]
to something that's 5% of the time, it's fine.

##### **Geohot** [[00:04:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=267)]
But do you see what I mean by like EGraph saturation?

##### **Geohot** [[00:04:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=273)]
You mean right in the EGraph algorithm?

##### **Qazalin** [[00:04:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=276)]
Yeah, the algorithm is simple, actually.

##### **Chenyu** [[00:04:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=279)]
It's not..

##### **Nimlgen** [[00:04:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=280)]
Basically what you do is you just like apply every rule.

##### **Qazalin** [[00:04:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=285)]
Every time you figure out which rules you can't,

##### **Geohot** [[00:04:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=287)]
you can apply and you apply every rule.

##### **Geohot** [[00:04:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=289)]
And then you use a clever data structure

##### **Geohot** [[00:04:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=291)]
in order to like not have to store the exponential number of graphs.

##### **Qazalin** [[00:04:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=296)]
Yeah, but how do you pick what you want at the end?

##### **Chenyu** [[00:05:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=300)]
So yeah, there is different algorithms for that.

##### **Nimlgen** [[00:05:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=303)]
But actually, it almost looks like choice.

##### **Qazalin** [[00:05:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=304)]
It's interesting how much it looks like choice, right?

##### **Geohot** [[00:05:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=307)]
Because you can like encode exponentials in everything

##### **Geohot** [[00:05:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=310)]
where you can say, well, okay, at this branch,

##### **Geohot** [[00:05:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=311)]
you can go, you know, any of these three things are equivalent.

##### **Qazalin** [[00:05:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=314)]
So it's just equivalence things at every node.

##### **Chenyu** [[00:05:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=318)]
Then at the end, you can run..

##### **Nimlgen** [[00:05:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=320)]
I haven't looked too much into that,

##### **Qazalin** [[00:05:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=321)]
but you can write like evaluation functions

##### **Geohot** [[00:05:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=326)]
that run in the runtime of the number of nodes,

##### **Geohot** [[00:05:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=330)]
not the number of graphs.

##### **Geohot** [[00:05:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=337)]
But yeah, again, if this is something you want me to spend time on,

##### **Qazalin** [[00:05:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=340)]
if it turns out to be ordering,

##### **Chenyu** [[00:05:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=342)]
because EGraphs will totally just fix the ordering stuff.

##### **Nimlgen** [[00:05:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=344)]
And I think we're going to have to go there eventually.

##### **Qazalin** [[00:05:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=346)]
But if the bug turns out,

##### **Geohot** [[00:05:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=347)]
to be something else,

##### **Geohot** [[00:05:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=348)]
then we can do it later.

##### **Geohot** [[00:05:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=350)]
Yeah, I will know better after I look at this more.

##### **Qazalin** [[00:05:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=353)]
So you can decide.

##### **Chenyu** [[00:05:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=354)]
The most exciting thing I learned about EGraphs

##### **Nimlgen** [[00:05:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=357)]
is that our existing rewrite rules work totally fine.

##### **Qazalin** [[00:06:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=361)]
That's a limitation.

##### **Geohot** [[00:06:02](https://www.youtube.com/watch?v=cLnu8McQRlw&t=362)]
The reason they don't work in egg is a limitation of egg,

##### **Geohot** [[00:06:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=364)]
not a limitation of the fundamental idea of EGraphs.

##### **Geohot** [[00:06:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=371)]
So that's the speed front

##### **Qazalin** [[00:06:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=375)]
and semi-related.

##### **Chenyu** [[00:06:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=377)]
Okay.

##### **Nimlgen** [[00:06:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=377)]
So I think Kama also expressed that they are interested in the edge event decode.

##### **Qazalin** [[00:06:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=385)]
Yeah.

##### **Geohot** [[00:06:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=386)]
Nimel, what do you think about that?

##### **Geohot** [[00:06:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=387)]
What do you got planned for this week?

##### **Geohot** [[00:06:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=393)]
Yeah, actually, I plan to look into this.

##### **Qazalin** [[00:06:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=398)]
Great.

##### **Chenyu** [[00:06:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=398)]
Yeah, I think Kama would be super happy with that.

##### **Nimlgen** [[00:06:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=404)]
How do we know if we support it well?

##### **Qazalin** [[00:06:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=406)]
Is there a top?

##### **Geohot** [[00:06:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=407)]
Is there something that we can try test?

##### **Geohot** [[00:06:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=410)]
Oh, I mean, it's the simplest thing to test.

##### **Geohot** [[00:06:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=414)]
Just decode an HVAC.

##### **Qazalin** [[00:06:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=416)]
Maybe some throughput tests.

##### **Chenyu** [[00:06:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=418)]
We can definitely..

##### **Nimlgen** [[00:06:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=419)]
There's tons of examples of Kama HVACs online we can try.

##### **Qazalin** [[00:07:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=423)]
But I mean, we should also test it with other HVACs too.

##### **Geohot** [[00:07:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=432)]
Another victory for Kama is

##### **Geohot** [[00:07:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=436)]
they do this..

##### **Geohot** [[00:07:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=437)]
they do this resizing thing on the device.

##### **Qazalin** [[00:07:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=441)]
And they have a custom open CL kernel for it.

##### **Chenyu** [[00:07:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=443)]
And now when you write it in TinyGrad, it's just fast.

##### **Nimlgen** [[00:07:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=450)]
Well, if you write it as a 2D indexing kernel, it's not fast.

##### **Qazalin** [[00:07:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=453)]
But if you flatten it first, and then you index in 1D, it's fast.

##### **Geohot** [[00:07:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=459)]
Why is it not fast for 2D? Do you know?

##### **Geohot** [[00:07:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=462)]
I have no idea. I think we just didn't write the..

##### **Geohot** [[00:07:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=466)]
I think we just didn't write the..

##### **Qazalin** [[00:07:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=467)]
We can fix that.

##### **Chenyu** [[00:07:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=470)]
But it's also not a big deal to flatten and reshape.

##### **Nimlgen** [[00:07:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=473)]
It's free.

##### **Qazalin** [[00:07:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=475)]
I updated a few tensor methods

##### **Geohot** [[00:07:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=478)]
to use ARange as building blocks

##### **Geohot** [[00:08:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=481)]
instead of movements.

##### **Geohot** [[00:08:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=483)]
I think it's identity metrics

##### **Qazalin** [[00:08:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=484)]
and the triangular thing.

##### **Chenyu** [[00:08:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=489)]
Those make the kernel itself a lot simpler and faster.

##### **Nimlgen** [[00:08:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=493)]
Great.

##### **Qazalin** [[00:08:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=495)]
ARange is basically a movement op.

##### **Geohot** [[00:08:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=497)]
We should do that.

##### **Geohot** [[00:08:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=497)]
We should feel free to use it.

##### **Geohot** [[00:08:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=500)]
So the main difference is

##### **Qazalin** [[00:08:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=503)]
if you don't use it

##### **Chenyu** [[00:08:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=506)]
and later the thing simplifies into ranges,

##### **Nimlgen** [[00:08:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=509)]
in uop level, that range will be reused.

##### **Qazalin** [[00:08:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=512)]
So think about when you do identity metrics.

##### **Geohot** [[00:08:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=517)]
It's either like

##### **Geohot** [[00:08:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=520)]
your x equals to your y, that's your identity.

##### **Geohot** [[00:08:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=525)]
But if that range is reused,

##### **Qazalin** [[00:08:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=526)]
you end up with a new one.

##### **Chenyu** [[00:08:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=527)]
You end up having a much more complicated expression

##### **Nimlgen** [[00:08:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=529)]
than just GID x0 equals to GID x1

##### **Qazalin** [[00:08:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=534)]
because that is reused.

##### **Geohot** [[00:08:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=537)]
I mean, I see how simple the ARange one is.

##### **Geohot** [[00:09:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=540)]
I struggle to even think about what the movement op one is.

##### **Geohot** [[00:09:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=543)]
I kind of know it, but yeah, it seems a lot more complicated.

##### **Qazalin** [[00:09:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=547)]
I think using ARange is fine.

##### **Chenyu** [[00:09:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=551)]
Yeah.

##### **Nimlgen** [[00:09:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=552)]
Okay.

##### **Qazalin** [[00:09:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=554)]
Let's look at comma.

##### **Geohot** [[00:09:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=555)]
Then we have MLPerf.

##### **Geohot** [[00:09:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=557)]
Then we have LLaMA.

##### **Geohot** [[00:09:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=563)]
There was a stop function.

##### **Qazalin** [[00:09:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=565)]
I tried to see what's the limit that we are getting now on LLaMA training.

##### **Chenyu** [[00:09:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=571)]
I think we are still 2x off in terms of memory usage.

##### **Nimlgen** [[00:09:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=578)]
Yeah.

##### **Qazalin** [[00:09:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=579)]
So I think there's three parts to LLaMA training that can be worked on in parallel.

##### **Geohot** [[00:09:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=583)]
One is getting 8B LLaMA to train,

##### **Geohot** [[00:09:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=586)]
which should work with what we already have.

##### **Geohot** [[00:09:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=593)]
Like just making sure that, you know, all our data loading is correct,

##### **Qazalin** [[00:09:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=597)]
that we're achieving the required loss.

##### **Chenyu** [[00:09:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=598)]
It's nice that it actually is an MLPerf thing.

##### **Nimlgen** [[00:10:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=600)]
So I think getting the 8B is one thing.

##### **Qazalin** [[00:10:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=605)]
Getting some form of flash attention kernel.

##### **Geohot** [[00:10:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=609)]
The sooner we can do this, the better.

##### **Geohot** [[00:10:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=611)]
Like the sooner we can get any flash attention in there,

##### **Geohot** [[00:10:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=613)]
because that will let us do the long context function.

##### **Qazalin** [[00:10:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=615)]
So we can actually do that in a single GPU.

##### **Chenyu** [[00:10:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=617)]
So even if we do..

##### **Nimlgen** [[00:10:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=618)]
By the way,

##### **Qazalin** [[00:10:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=620)]
Klausulin has this cute thing where you can actually..

##### **Geohot** [[00:10:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=622)]
You can use custom kernels if you want to just write arbitrary like hip code

##### **Geohot** [[00:10:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=627)]
by using the custom UOP,

##### **Geohot** [[00:10:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=629)]
which again I think is totally fine for just getting some sort of flash attention in there

##### **Qazalin** [[00:10:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=634)]
as soon as possible.

##### **Chenyu** [[00:10:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=636)]
So we can start training 8B.

##### **Nimlgen** [[00:10:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=639)]
So there's the 8B training.

##### **Qazalin** [[00:10:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=641)]
There's the fast kernels,

##### **Geohot** [[00:10:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=643)]
which is like, you know, getting fast flash attention.

##### **Geohot** [[00:10:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=645)]
First, and then fast GEMM.

##### **Geohot** [[00:10:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=648)]
Second.

##### **Qazalin** [[00:10:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=649)]
And then there is the outer world stuff.

##### **Chenyu** [[00:10:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=653)]
So I spent a couple hours reading how Jax does scan and 4i.

##### **Nimlgen** [[00:11:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=660)]
They're both differentiable.

##### **Qazalin** [[00:11:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=663)]
So it depends actually.

##### **Geohot** [[00:11:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=665)]
Jax has a whole lot of code paths to deal with this.

##### **Geohot** [[00:11:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=668)]
In the simple code path,

##### **Geohot** [[00:11:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=669)]
they will happily differentiate scan.

##### **Qazalin** [[00:11:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=672)]
And the derivative is pretty simple.

##### **Chenyu** [[00:11:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=674)]
What you do is..

##### **Nimlgen** [[00:11:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=675)]
You convert the range..

##### **Qazalin** [[00:11:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=678)]
All you basically need to do is substitute the range on the forward pass

##### **Geohot** [[00:11:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=682)]
with a gradient range on the backwards pass.

##### **Geohot** [[00:11:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=685)]
And then it mostly just works.

##### **Geohot** [[00:11:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=688)]
You can't use the same range on the forward pass as the backward pass

##### **Qazalin** [[00:11:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=692)]
because then it's..

##### **Chenyu** [[00:11:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=694)]
You know, then the range already ended.

##### **Nimlgen** [[00:11:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=697)]
So you just replace the range and then the gradient rule is simple.

##### **Qazalin** [[00:11:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=700)]
So that's cool.

##### **Geohot** [[00:11:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=701)]
As soon as we get a scan operator that works.

##### **Geohot** [[00:11:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=703)]
So I should have that by the end of this week.

##### **Geohot** [[00:11:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=705)]
That's my main focus.

##### **Qazalin** [[00:11:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=706)]
And then we'll be able to write these things.

##### **Chenyu** [[00:11:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=708)]
It'll be the same thing,

##### **Nimlgen** [[00:11:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=709)]
but it'll just be very fast to..

##### **Qazalin** [[00:11:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=712)]
In Python time.

##### **Geohot** [[00:11:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=714)]
Because we don't have to differentiate this massive graph.

##### **Geohot** [[00:11:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=717)]
And we don't have to rangeify this massive graph.

##### **Geohot** [[00:11:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=719)]
Which are both slow.

##### **Qazalin** [[00:12:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=724)]
But yeah.

##### **Chenyu** [[00:12:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=725)]
Yeah, if you think we can get any blockers to get 8b training

##### **Nimlgen** [[00:12:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=730)]
on par with the ML protocols.

##### **Qazalin** [[00:12:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=734)]
Oh.

##### **Geohot** [[00:12:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=735)]
Yeah.

##### **Geohot** [[00:12:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=735)]
I would test with now later today to see what's the current memory usage

##### **Geohot** [[00:12:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=740)]
even for 8b.

##### **Qazalin** [[00:12:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=742)]
Last time I checked it was pretty big.

##### **Chenyu** [[00:12:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=746)]
BoseParrot, you think you could have a flash attention kernel

##### **Nimlgen** [[00:12:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=749)]
in any way, shape or form up by the end of the week?

##### **Qazalin** [[00:12:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=754)]
Yeah, that should be fine.

##### **Geohot** [[00:12:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=756)]
I probably can actually have a HIP one maybe by today or tomorrow.

##### **Geohot** [[00:12:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=762)]
Great.

##### **Geohot** [[00:12:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=763)]
Yeah.

##### **Qazalin** [[00:12:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=764)]
I mean, even if it's the slow one from the 4090 though,

##### **Chenyu** [[00:12:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=767)]
that one's good too.

##### **Nimlgen** [[00:12:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=768)]
It's just important that we get the memory usage correct.

##### **Qazalin** [[00:12:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=771)]
Yeah.

##### **Geohot** [[00:12:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=773)]
I mean, anything will be faster than using the massive amount of memory anyway.

##### **Geohot** [[00:12:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=776)]
So yeah, whatever we can get in.

##### **Geohot** [[00:12:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=778)]
But let's definitely..

##### **Qazalin** [[00:12:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=779)]
I want this training by the end of the week with a custom flash forward

##### **Chenyu** [[00:13:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=783)]
and flash backwards to not waste tons of RAM.

##### **Nimlgen** [[00:13:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=790)]
And also we need that so when I'm writing the scan thing,

##### **Qazalin** [[00:13:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=792)]
I make sure it still works.

##### **Geohot** [[00:13:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=794)]
It's a little bit tricky on the scan derivative.

##### **Geohot** [[00:13:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=796)]
So the naive way to write it,

##### **Geohot** [[00:13:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=798)]
it's going to recompute everything from the forward pass.

##### **Qazalin** [[00:13:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=804)]
So yeah, I mean, in some ways that's gradient checkpointing for free.

##### **Chenyu** [[00:13:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=809)]
In other ways, it's, well, it's not explicit.

##### **Nimlgen** [[00:13:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=812)]
So yeah, I mean, I think that flash attention forward saves the soft maxes.

##### **Qazalin** [[00:13:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=820)]
I have to make sure that we have a way to do that.

##### **Geohot** [[00:13:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=827)]
So yeah, I think that's pretty much it.

##### **Geohot** [[00:13:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=828)]
So yeah, I think that's pretty much it.

##### **Geohot** [[00:13:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=828)]
Another thing that will help is FP8.

##### **Qazalin** [[00:13:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=832)]
So I have a checklist on my friend details.

##### **Chenyu** [[00:13:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=836)]
I clearly have FP8.

##### **Nimlgen** [[00:14:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=841)]
Video one has to be FP8.

##### **Qazalin** [[00:14:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=843)]
So it would be great if there's just a recipe we could copy.

##### **Geohot** [[00:14:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=847)]
Though there's a chance it's not FP8 and it's block scalars.

##### **Geohot** [[00:14:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=853)]
Yeah.

##### **Geohot** [[00:14:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=855)]
Yeah, if it's block scalars.

##### **Qazalin** [[00:14:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=857)]
Yeah.

##### **Chenyu** [[00:14:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=860)]
Cool.

##### **Nimlgen** [[00:14:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=864)]
Sounds good.

##### **Qazalin** [[00:14:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=868)]
So some kind of custom, doesn't need to be slow,

##### **Geohot** [[00:14:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=873)]
but need to be good on memory, flash attention forward and backward,

##### **Geohot** [[00:14:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=876)]
then running Lava HP.

##### **Geohot** [[00:14:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=880)]
Yeah, that would be great.

##### **Qazalin** [[00:14:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=884)]
Sorry, go ahead.

##### **Chenyu** [[00:14:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=886)]
I mean, things that I definitely want by the end of the year.

##### **Nimlgen** [[00:14:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=890)]
I want like custom flash attention and GEMM working that are decently fast.

##### **Qazalin** [[00:14:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=897)]
I want 8B training and hitting the ML perf target.

##### **Geohot** [[00:15:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=900)]
And I want four or five B having a Python time of like under 20 seconds

##### **Geohot** [[00:15:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=905)]
or something we can iterate on.

##### **Geohot** [[00:15:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=912)]
But yeah.

##### **Qazalin** [[00:15:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=912)]
If we can.

##### **Chenyu** [[00:15:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=913)]
Yeah.

##### **Nimlgen** [[00:15:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=917)]
Go ahead.

##### **Qazalin** [[00:15:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=918)]
Oh, no.

##### **Geohot** [[00:15:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=919)]
I was going to conclude the point.

##### **Geohot** [[00:15:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=920)]
You go ahead.

##### **Geohot** [[00:15:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=923)]
Oh, yeah.

##### **Qazalin** [[00:15:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=923)]
No, that's, I mean, yeah, just basically that.

##### **Chenyu** [[00:15:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=925)]
Like, this is where we got to be by the end of the year.

##### **Nimlgen** [[00:15:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=927)]
I think we can do it.

##### **Qazalin** [[00:15:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=927)]
We got six weeks.

##### **Geohot** [[00:15:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=932)]
Sounds good.

##### **Geohot** [[00:15:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=935)]
Next is SQTT with the Vibe processor.

##### **Geohot** [[00:15:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=946)]
Yeah, I can talk about my site on SQTT. I merged the..

##### **Qazalin** [[00:15:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=956)]
Can I hear you?

##### **Chenyu** [[00:16:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=970)]
Can you hear me now?

##### **Nimlgen** [[00:16:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=972)]
Yes.

##### **Qazalin** [[00:16:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=974)]
All right. I can talk about my site. I merged the timeline. So if you run with SQTT equals one,

##### **Geohot** [[00:16:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=983)]
you can see the timeline in the x-axis.

##### **Geohot** [[00:16:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=987)]
This is the cycles of all the waves that are launching.

##### **Geohot** [[00:16:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=991)]
How did you sync the cycles to the time?

##### **Qazalin** [[00:16:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=995)]
Oh, it's actually just cycles on the x-axis. I don't sync to time.

##### **Chenyu** [[00:16:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1002)]
Oh, I see. So it's a separate graph. It's not on the main profiler.

##### **Nimlgen** [[00:16:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1005)]
It's not on the main profiler.

##### **Qazalin** [[00:16:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1009)]
That's fine, actually. I think that's mostly fine. So it's cool.

##### **Geohot** [[00:16:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1012)]
You've got something like.. I can't run it right now on my Mac, but I'll try it later.

##### **Geohot** [[00:16:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1017)]
So that's..

##### **Geohot** [[00:16:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1017)]
You're saying that's like when I click on the kernel, it shows me how all the waves dispatched on a separate copy of the profile timeline?

##### **Qazalin** [[00:17:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1025)]
Yeah, there's a picture of it on this channel if you want to look at it.

##### **Chenyu** [[00:17:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1029)]
Yeah, yeah. I was looking at it. I didn't totally follow where those things were.

##### **Nimlgen** [[00:17:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1032)]
Oh, I see. Okay, cool. So you click on the kernel and it shows the waves. Yeah, that's great.

##### **Qazalin** [[00:17:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1036)]
Yeah, yeah.

##### **Geohot** [[00:17:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1038)]
Yeah.

##### **Geohot** [[00:17:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1041)]
I actually think it's better because when I normalized it to..

##### **Geohot** [[00:17:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1047)]
Real time, it looked too small.

##### **Qazalin** [[00:17:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1051)]
Like it's so granular.

##### **Chenyu** [[00:17:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1054)]
It has to be like a clock scale.

##### **Nimlgen** [[00:17:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1057)]
Yeah, I mean, it's super fast.

##### **Qazalin** [[00:17:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1060)]
So like this is going to be..

##### **Geohot** [[00:17:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1062)]
You got to think about like what the order of magnitude is of the number of waves we're going to do.

##### **Geohot** [[00:17:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1066)]
The order of magnitude is something like 10,000.

##### **Geohot** [[00:17:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1068)]
Is it fine?

##### **Qazalin** [[00:17:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1069)]
Can our profile..

##### **Chenyu** [[00:17:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1070)]
Like that's reusing the logic from profiler, right?

##### **Nimlgen** [[00:17:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1074)]
Yeah, everything is reusing.

##### **Qazalin** [[00:17:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1076)]
Great.

##### **Geohot** [[00:17:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1076)]
Yeah.

##### **Geohot** [[00:17:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1077)]
Yeah, I think this is the right move.

##### **Geohot** [[00:17:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1079)]
I think we shouldn't try to shove it onto the top graph.

##### **Qazalin** [[00:18:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1081)]
I think that's a lot more than we need.

##### **Chenyu** [[00:18:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1084)]
Like if anything, the only thing we might want to put on the top graph is some kind of checkpoints.

##### **Nimlgen** [[00:18:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1087)]
But I think those should be in GPU time anyway.

##### **Qazalin** [[00:18:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1088)]
So yeah, totally fine with it being a separate thing.

##### **Geohot** [[00:18:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1092)]
And yeah, like order of magnitude.

##### **Geohot** [[00:18:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1094)]
Can we handle something like 10,000 waves?

##### **Geohot** [[00:18:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1100)]
10,000 waves.

##### **Qazalin** [[00:18:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1101)]
I think so.

##### **Chenyu** [[00:18:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1102)]
Yeah, that should be fine.

##### **Nimlgen** [[00:18:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1104)]
Yeah, it'd be really cool.

##### **Qazalin** [[00:18:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1105)]
Like if you could like click on the wave and see each one.

##### **Geohot** [[00:18:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1107)]
And then like average some statistics about the instruction.

##### **Geohot** [[00:18:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1110)]
But also be able to look at each individual one.

##### **Geohot** [[00:18:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1112)]
You get so much information from these GPUs.

##### **Qazalin** [[00:18:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1118)]
Did you manage to do the reversing?

##### **Chenyu** [[00:18:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1121)]
Oh, did you try it?

##### **Nimlgen** [[00:18:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1122)]
Uh-huh.

##### **Qazalin** [[00:18:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1123)]
I mean, I looked at it a little bit.

##### **Geohot** [[00:18:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1125)]
I can't really decode it per se.

##### **Geohot** [[00:18:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1129)]
Yeah, yeah, yeah.

##### **Geohot** [[00:18:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1130)]
I got it mostly.

##### **Qazalin** [[00:18:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1133)]
But there's no like stall in the..

##### **Chenyu** [[00:18:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1137)]
Well, no, there's no stall.

##### **Nimlgen** [[00:19:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1140)]
There's no stall.

##### **Qazalin** [[00:19:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1141)]
The big breakthrough I made was being able to..

##### **Geohot** [[00:19:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1143)]
I got all the names of the things from the..

##### **Geohot** [[00:19:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1147)]
Just by excluding them one at a time.

##### **Geohot** [[00:19:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1149)]
Because there's a named enum to exclude them.

##### **Qazalin** [[00:19:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1152)]
So there's not going to be a stall.

##### **Chenyu** [[00:19:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1153)]
But that's computed all by the RockM profile trace.

##### **Nimlgen** [[00:19:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1157)]
You basically just know when each instruction ran.

##### **Qazalin** [[00:19:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1161)]
You know when the instruction dispatched and when the instruction ran.

##### **Geohot** [[00:19:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1164)]
And stall is just dispatch.

##### **Geohot** [[00:19:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1167)]
Sorry, run minus dispatch minus the time it takes to run the instruction.

##### **Geohot** [[00:19:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1175)]
We don't know the time it takes to run the instruction?

##### **Qazalin** [[00:19:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1179)]
No, we don't.

##### **Chenyu** [[00:19:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1180)]
My guess would be that there's profiles.

##### **Nimlgen** [[00:19:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1182)]
That there's tables embedded in.

##### **Qazalin** [[00:19:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1185)]
Table, yeah.

##### **Geohot** [[00:19:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1186)]
Yeah, I don't know.

##### **Geohot** [[00:19:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1187)]
I don't think we have to use the raw one.

##### **Geohot** [[00:19:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1188)]
This wasn't something I did during the week.

##### **Qazalin** [[00:19:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1191)]
This was just fun for the weekend.

##### **Chenyu** [[00:19:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1196)]
Yeah, it's kind of cute.

##### **Nimlgen** [[00:19:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1197)]
What the format is.

##### **Qazalin** [[00:19:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1198)]
It's all nibble based.

##### **Geohot** [[00:19:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1199)]
So it's all four bit based.

##### **Geohot** [[00:20:02](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1202)]
And then, yeah.

##### **Geohot** [[00:20:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1204)]
It uses this shift register.

##### **Qazalin** [[00:20:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1206)]
It's very hardware.

##### **Chenyu** [[00:20:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1208)]
It looks very hardware.

##### **Nimlgen** [[00:20:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1209)]
Yeah, so I got all the stuff decoding.

##### **Qazalin** [[00:20:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1212)]
If you're ever confused about what's going on in the big profile.

##### **Geohot** [[00:20:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1216)]
You can run this and actually take a look at what it's using to build that.

##### **Geohot** [[00:20:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1223)]
Yeah, it also shows us how we might be able to disable stuff.

##### **Geohot** [[00:20:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1226)]
To make things smaller.

##### **Qazalin** [[00:20:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1227)]
Or whatever.

##### **Chenyu** [[00:20:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1229)]
But no, overall, it's that rock him.

##### **Nimlgen** [[00:20:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1232)]
Rock him.

##### **Qazalin** [[00:20:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1232)]
Trace decoder.

##### **Geohot** [[00:20:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1233)]
Assuming it's stable is giving us a lot of good stuff.

##### **Geohot** [[00:20:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1236)]
I think we just hope they open source it.

##### **Geohot** [[00:20:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1245)]
Yeah, I don't know.

##### **Qazalin** [[00:20:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1247)]
It's quite hard with the callback pattern that they're using to make stuff.

##### **Chenyu** [[00:20:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1254)]
Incremental decoding.

##### **Nimlgen** [[00:20:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1255)]
Yeah, right now.

##### **Qazalin** [[00:20:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1256)]
I'm parsing.

##### **Geohot** [[00:20:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1257)]
I think up for.

##### **Geohot** [[00:20:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1258)]
I'm not asking for stuff to be incremental.

##### **Geohot** [[00:21:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1260)]
What I'm asking for is currently you're running the trace decode before Viz even starts.

##### **Qazalin** [[00:21:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1266)]
It shouldn't run the trace decode until I click on the kernel encounters.

##### **Chenyu** [[00:21:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1271)]
But if you click away, I can't control see it.

##### **Nimlgen** [[00:21:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1275)]
That's okay.

##### **Qazalin** [[00:21:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1276)]
But.

##### **Geohot** [[00:21:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1276)]
Yeah, so for the control C, actually, the only way I found is using threading.

##### **Geohot** [[00:21:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1284)]
So, yeah.

##### **Geohot** [[00:21:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1285)]
And that using what?

##### **Qazalin** [[00:21:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1287)]
Yeah.

##### **Chenyu** [[00:21:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1288)]
Threading.

##### **Nimlgen** [[00:21:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1288)]
Threading.

##### **Qazalin** [[00:21:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1288)]
Like to put this rock him profile into separate thread.

##### **Geohot** [[00:21:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1292)]
Oh, you put it in separate thread and you like P thread kill it?

##### **Geohot** [[00:21:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1296)]
Yeah, cool.

##### **Geohot** [[00:21:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1298)]
And that seems fine, too.

##### **Qazalin** [[00:21:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1301)]
But unless we're going to start the decoding when you click on the counter thing.

##### **Chenyu** [[00:21:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1307)]
Yes, because I'm less worried about the annoying thing now is like if there's 20 kernels and they're all kind of big.

##### **Nimlgen** [[00:21:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1314)]
It takes, you know.

##### **Qazalin** [[00:21:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1316)]
30 seconds.

##### **Geohot** [[00:21:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1317)]
30 seconds to start this.

##### **Geohot** [[00:21:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1318)]
We can never have that.

##### **Geohot** [[00:21:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1319)]
This always needs to come up instantly and then can spend time decoding this stuff later.

##### **Qazalin** [[00:22:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1330)]
If you can't control see it, that's a limitation.

##### **Chenyu** [[00:22:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1332)]
But I think threading and P thread kill is pretty good, too.

##### **Nimlgen** [[00:22:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1337)]
Like, it's better that you can't control see it when I click away.

##### **Qazalin** [[00:22:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1340)]
Then this takes a long time to start up.

##### **Geohot** [[00:22:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1347)]
Makes sense.

##### **Geohot** [[00:22:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1348)]
Yeah.

##### **Geohot** [[00:22:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1350)]
And actually, I'll just say that we have separate test QTT profile events for different launches.

##### **Qazalin** [[00:22:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1358)]
So it should be pretty easy to.

##### **Chenyu** [[00:22:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1362)]
Like to parse the blobs you need.

##### **Nimlgen** [[00:22:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1366)]
Oh, yeah.

##### **Qazalin** [[00:22:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1367)]
I mean, that's all.

##### **Geohot** [[00:22:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1368)]
Yeah, I looked at that.

##### **Geohot** [[00:22:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1370)]
It's per kernel and it's per shader engine.

##### **Geohot** [[00:22:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1372)]
So we can totally.

##### **Qazalin** [[00:22:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1375)]
Totally.

##### **Chenyu** [[00:22:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1379)]
I mean, the format's incredible.

##### **Nimlgen** [[00:23:02](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1382)]
Like, it's logging literally two things for every instruction.

##### **Qazalin** [[00:23:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1393)]
I still don't exactly understand how to recover what the PC of the GPU is.

##### **Geohot** [[00:23:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1397)]
I think you might actually just have to count them all.

##### **Geohot** [[00:23:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1399)]
But.

##### **Geohot** [[00:23:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1403)]
Like, it doesn't tell you the PC.

##### **Qazalin** [[00:23:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1404)]
It logs nothing you don't need.

##### **Chenyu** [[00:23:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1407)]
They really made this format super minimal.

##### **Nimlgen** [[00:23:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1411)]
And.

##### **Qazalin** [[00:23:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1414)]
Yeah, cool.

##### **Geohot** [[00:23:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1415)]
Good progress.

##### **Geohot** [[00:23:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1415)]
Hopefully we can start using this to debug and make our kernels faster.

##### **Geohot** [[00:23:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1419)]
Oh, the one that I really want you to test this stuff on is AMD UOP MatMall.

##### **Qazalin** [[00:23:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1424)]
It should be, like, decently fast and usable with AMD UOP MatMall.

##### **Chenyu** [[00:23:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1429)]
You don't have to run the MatMall 10 times.

##### **Nimlgen** [[00:23:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1436)]
Good.

##### **Qazalin** [[00:23:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1436)]
Yeah.

##### **Geohot** [[00:23:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1438)]
It's a very big one.

##### **Geohot** [[00:24:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1440)]
That's the scale we need to be targeting.

##### **Geohot** [[00:24:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1443)]
I mean, it's not crazy big.

##### **Qazalin** [[00:24:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1444)]
It's a much smaller MatMall than any of the LLaMA ones.

##### **Chenyu** [[00:24:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1450)]
Yeah, so we get every hit of the instruction.

##### **Nimlgen** [[00:24:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1455)]
So it's going to be a couple.

##### **Qazalin** [[00:24:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1459)]
I'll test it.

##### **Geohot** [[00:24:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1461)]
Cool.

##### **Geohot** [[00:24:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1462)]
Yeah, I mean, we can also.

##### **Geohot** [[00:24:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1464)]
SQTT lets you disable a lot of stuff.

##### **Qazalin** [[00:24:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1465)]
Like, you can disable.

##### **Chenyu** [[00:24:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1466)]
Instructions.

##### **Nimlgen** [[00:24:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1467)]
We can disable registers.

##### **Qazalin** [[00:24:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1469)]
Like, you know, the most important thing to first get is just literally wave start and wave end.

##### **Geohot** [[00:24:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1473)]
And that's pretty small.

##### **Geohot** [[00:24:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1474)]
So.

##### **Geohot** [[00:24:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1474)]
I don't know.

##### **Qazalin** [[00:24:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1476)]
Oh, that's very.

##### **Chenyu** [[00:24:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1477)]
That's very small.

##### **Nimlgen** [[00:24:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1478)]
Yeah.

##### **Qazalin** [[00:24:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1479)]
Yeah.

##### **Geohot** [[00:24:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1480)]
Like, maybe we can have an SQTT equals one and an SQTT equals two, depending on what you want to say.

##### **Geohot** [[00:24:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1485)]
I actually have a prototype of instead of decoding the instructions array that the decoder gives us.

##### **Geohot** [[00:24:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1495)]
Instead of, like, parsing.

##### **Qazalin** [[00:24:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1496)]
Into the array, which we right now do.

##### **Chenyu** [[00:24:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1499)]
We just copy the entire block.

##### **Nimlgen** [[00:25:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1503)]
Into Python and then.

##### **Qazalin** [[00:25:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1507)]
Decode the instructions later.

##### **Geohot** [[00:25:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1508)]
And that's very fast.

##### **Geohot** [[00:25:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1511)]
Cool.

##### **Geohot** [[00:25:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1513)]
Yeah.

##### **Qazalin** [[00:25:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1514)]
Yeah.

##### **Chenyu** [[00:25:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1515)]
I want it to be usable and decently fast on AMD MatMall.

##### **Nimlgen** [[00:25:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1518)]
Like if I was using this to iterate on that.

##### **Qazalin** [[00:25:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1523)]
Sounds good.

##### **Geohot** [[00:25:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1525)]
Cool.

##### **Geohot** [[00:25:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1529)]
Yeah.

##### **Geohot** [[00:25:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1529)]
Yeah.

##### **Qazalin** [[00:25:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1532)]
Yeah.

##### **Chenyu** [[00:25:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1533)]
That's SQTT.

##### **Nimlgen** [[00:25:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1534)]
We briefly touch on the flash attention of what's very have anything.

##### **Qazalin** [[00:25:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1540)]
Copy.

##### **Geohot** [[00:25:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1542)]
Uh.

##### **Geohot** [[00:25:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1546)]
Most of the stuff is good.

##### **Geohot** [[00:25:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1548)]
I have a PR for some MI three 50 support in tiny kittens.

##### **Qazalin** [[00:25:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1555)]
The main thing we're missing right now.

##### **Chenyu** [[00:25:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1556)]
Is just shared memory swizzling for.

##### **Nimlgen** [[00:26:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1560)]
Your memory bank conflicts.

##### **Qazalin** [[00:26:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1564)]
A lot of the hip kitchen stuff is a little annoying.

##### **Geohot** [[00:26:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1568)]
I would.

##### **Geohot** [[00:26:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1569)]
I don't want to go to assembly and a lot of their kernels go down to assembly.

##### **Geohot** [[00:26:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1575)]
In order to hit Max perf.

##### **Qazalin** [[00:26:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1577)]
I'm hoping that we can get some decent performance without having to do that.

##### **Chenyu** [[00:26:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1584)]
We'll see.

##### **Nimlgen** [[00:26:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1589)]
Yeah.

##### **Qazalin** [[00:26:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1590)]
Yeah.

##### **Geohot** [[00:26:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1590)]
I'm totally fine with getting like 80% as long as it's not 40%.

##### **Geohot** [[00:26:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1597)]
Yeah.

##### **Geohot** [[00:26:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1599)]
We can.

##### **Qazalin** [[00:26:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1600)]
We can look if the.

##### **Chenyu** [[00:26:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1601)]
It's interesting what they uncovered that the depending on the size of the load.

##### **Nimlgen** [[00:26:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1606)]
It determines how it accesses the banks.

##### **Qazalin** [[00:26:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1609)]
Just.

##### **Geohot** [[00:26:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1610)]
Yeah.

##### **Geohot** [[00:26:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1611)]
I mean, that's crazy.

##### **Geohot** [[00:26:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1612)]
Like.

##### **Qazalin** [[00:26:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1614)]
I don't just LLVM even like support.

##### **Chenyu** [[00:26:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1616)]
I don't even know.

##### **Nimlgen** [[00:26:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1616)]
I think the.

##### **Qazalin** [[00:27:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1620)]
I think the other one he's talking about.

##### **Geohot** [[00:27:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1621)]
Yeah.

##### **Geohot** [[00:27:02](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1622)]
Yeah.

##### **Geohot** [[00:27:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1623)]
Yeah.

##### **Qazalin** [[00:27:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1623)]
Yeah.

##### **Chenyu** [[00:27:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1624)]
I mean, I've never heard of it.

##### **Nimlgen** [[00:27:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1625)]
Like a chip doing that.

##### **Qazalin** [[00:27:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1632)]
I mean, you have to think about like what it is in there.

##### **Geohot** [[00:27:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1635)]
And they were like memory dispatch that like, why does that affect what banks that can access?

##### **Geohot** [[00:27:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1641)]
I don't really understand that.

##### **Geohot** [[00:27:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1643)]
Yeah.

##### **Qazalin** [[00:27:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1644)]
Yeah.

##### **Chenyu** [[00:27:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1644)]
Yeah.

##### **Nimlgen** [[00:27:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1647)]
But yeah, regardless, I don't think we should have to go down to assembly.

##### **Qazalin** [[00:27:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1652)]
Just make sure your memory patterns are exactly the same.

##### **Geohot** [[00:27:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1657)]
It'd be cool to get the real one building too, as a custom kernel, and then we can compare them in sqgt and stuff.

##### **Geohot** [[00:27:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1663)]
I did try that. The hip compiler is annoying to get working.

##### **Geohot** [[00:27:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1672)]
I ran into a bunch of include errors.

##### **Qazalin** [[00:27:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1676)]
Yeah, I mean, I don't know. Their matmul example didn't work.

##### **Chenyu** [[00:28:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1681)]
Their matmul example, I think they tested things on 7.0, and then on 7.1 it broke.

##### **Nimlgen** [[00:28:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1688)]
And it didn't break the compiler. It just started giving wrong answers.

##### **Qazalin** [[00:28:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1692)]
Which is.. I don't know.

##### **Geohot** [[00:28:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1699)]
Maybe next weekend I'll try an assembly backend.

##### **Geohot** [[00:28:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1704)]
We'll see how much progress I can make.

##### **Geohot** [[00:28:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1708)]
We have a secretly good Docker container.

##### **Qazalin** [[00:28:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1714)]
AMD has a secretly good Docker container? Is that what they're saying?

##### **Chenyu** [[00:28:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1718)]
Yeah, too late.

##### **Nimlgen** [[00:28:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1720)]
I don't know.

##### **Qazalin** [[00:28:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1723)]
Okay.

##### **Geohot** [[00:28:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1728)]
You just look at the way that matmul is written, and it doesn't look like the CUDA one.

##### **Geohot** [[00:28:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1733)]
It's clear how..

##### **Geohot** [[00:28:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1734)]
It's not just performance impact. It's actually wrong.

##### **Qazalin** [[00:28:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1738)]
Which..

##### **Chenyu** [[00:28:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1738)]
Yeah.

##### **Nimlgen** [[00:29:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1744)]
Okay.

##### **Qazalin** [[00:29:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1745)]
But also, the kittens people don't seem..

##### **Geohot** [[00:29:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1748)]
They seem to be researchers.

##### **Geohot** [[00:29:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1750)]
They seem just interested in achieving max perf on one..

##### **Geohot** [[00:29:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1753)]
Works on my machine is good enough for them.

##### **Qazalin** [[00:29:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1755)]
Stop.

##### **Chenyu** [[00:29:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1759)]
Hm.

##### **Nimlgen** [[00:29:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1763)]
I don't know.

##### **Qazalin** [[00:29:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1764)]
Okay.

##### **Geohot** [[00:29:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1765)]
I mean, it's what it is.

##### **Geohot** [[00:29:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1767)]
It's nice that there are people trying to get max perf.

##### **Geohot** [[00:29:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1770)]
Yeah.

##### **Qazalin** [[00:29:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1773)]
Okay.

##### **Chenyu** [[00:29:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1774)]
So..

##### **Nimlgen** [[00:29:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1776)]
Color bonkies..

##### **Qazalin** [[00:29:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1780)]
What did we get?

##### **Geohot** [[00:29:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1782)]
Wanna talk about the autogen stuff?

##### **Geohot** [[00:29:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1784)]
Yeah, I mean, the autogen stuff has merged.

##### **Geohot** [[00:29:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1787)]
It's kind of nice because we got to clean up a lot of the Objective-C stuff.

##### **Qazalin** [[00:29:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1792)]
There's still, like, one or two things that, like, still have to do, like, the manual message send.

##### **Chenyu** [[00:29:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1799)]
What's the manual message send?

##### **Nimlgen** [[00:30:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1801)]
Like, you have to do, obviously, underscore message send for a couple string manipulation things.

##### **Qazalin** [[00:30:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1807)]
Because it uses..

##### **Geohot** [[00:30:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1808)]
The string manipulation in Objective-C uses categories, I think they're called.

##### **Geohot** [[00:30:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1814)]
I put a comment about this.

##### **Geohot** [[00:30:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1816)]
Oh, yeah.

##### **Qazalin** [[00:30:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1817)]
Did you get that one? Yeah, yeah, yeah.

##### **Chenyu** [[00:30:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1820)]
Yeah, I don't know what's up with that.

##### **Nimlgen** [[00:30:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1821)]
Anyway, I wrote a patch that fixes it.

##### **Qazalin** [[00:30:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1823)]
It's not a problem with the real autogen because the real autogen generates stuff that looks like that rather than putting them inside the thing.

##### **Geohot** [[00:30:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1830)]
I can try and figure out..

##### **Geohot** [[00:30:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1830)]
What do you mean, the real autogen?

##### **Geohot** [[00:30:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1833)]
Like, the script generates code that..

##### **Qazalin** [[00:30:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1835)]
Or, like, the support slash autogen generates code that looks like the thing I posted right there.

##### **Chenyu** [[00:30:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1840)]
Whereas the test was..

##### **Nimlgen** [[00:30:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1842)]
I put the fields inside..

##### **Qazalin** [[00:30:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1843)]
Oh, I see what you're saying.

##### **Geohot** [[00:30:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1844)]
So it was just the test.

##### **Geohot** [[00:30:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1844)]
Oh, cool.

##### **Geohot** [[00:30:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1845)]
Yeah.

##### **Qazalin** [[00:30:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1847)]
Yeah, so it's not a..

##### **Chenyu** [[00:30:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1848)]
It's not a..

##### **Nimlgen** [[00:30:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1848)]
It's not a real issue.

##### **Qazalin** [[00:30:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1849)]
Yeah.

##### **Geohot** [[00:30:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1850)]
I mean, I could try and figure out exactly what's going on there because it should work, but..

##### **Geohot** [[00:30:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1853)]
I don't know.

##### **Geohot** [[00:30:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1857)]
Yeah, yeah.

##### **Qazalin** [[00:30:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1858)]
So, anyway, yeah, there's these Objective-C categories which we could try and parse as well, but it just seemed annoying and also, like, is only used in, like, three places, so..

##### **Chenyu** [[00:31:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1867)]
Just make the escape patch code clean and..

##### **Nimlgen** [[00:31:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1869)]
Yeah.

##### **Qazalin** [[00:31:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1871)]
Yeah.

##### **Geohot** [[00:31:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1875)]
I don't know if there's anything else with autogen right now.

##### **Geohot** [[00:31:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1878)]
The nice thing is that..

##### **Geohot** [[00:31:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1879)]
I think you mentioned this last time, but it's easy to edit it now because it's just Intree and it's not, like..

##### **Qazalin** [[00:31:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1884)]
Yeah, no, that library was bad to rely on.

##### **Chenyu** [[00:31:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1888)]
Yeah.

##### **Nimlgen** [[00:31:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1889)]
I mean, it was fine at the beginning, but it kind of got out of control.

##### **Qazalin** [[00:31:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1891)]
Yeah.

##### **Geohot** [[00:31:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1891)]
No, it was said script.

##### **Geohot** [[00:31:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1892)]
The said editing of the outputted thing really got out of control.

##### **Geohot** [[00:31:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1896)]
Yeah.

##### **Qazalin** [[00:31:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1897)]
So, cool.

##### **Chenyu** [[00:31:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1898)]
Well, that's that.

##### **Nimlgen** [[00:31:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1898)]
Yeah.

##### **Qazalin** [[00:31:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1901)]
Other bounties.

##### **Geohot** [[00:31:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1902)]
It looks like there's progress on the torch bounty.

##### **Geohot** [[00:31:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1906)]
Yeah.

##### **Geohot** [[00:31:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1907)]
Yeah.

##### **Qazalin** [[00:31:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1907)]
So, I'm going to go ahead and do a little bit of a re-locking, which is good.

##### **Chenyu** [[00:31:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1909)]
I will re-lock that.

##### **Nimlgen** [[00:31:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1910)]
Don't tell me that it was fast enough.

##### **Qazalin** [[00:31:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1912)]
I know how fast it used to be.

##### **Geohot** [[00:31:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1913)]
It used to be good, so we got to make it good again.

##### **Geohot** [[00:31:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1916)]
But, yeah, looks like we'll get that back soon.

##### **Geohot** [[00:32:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1923)]
What else we got?

##### **Qazalin** [[00:32:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1928)]
There's some update on the Winogre one, it seems.

##### **Chenyu** [[00:32:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1934)]
Is it ready to merge?

##### **Nimlgen** [[00:32:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1935)]
Yeah.

##### **Qazalin** [[00:32:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1935)]
I pinged about that.

##### **Geohot** [[00:32:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1937)]
I love that.

##### **Geohot** [[00:32:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1937)]
I went through all the pull requests.

##### **Geohot** [[00:32:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1938)]
I went through all the pull requests.

##### **Qazalin** [[00:32:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1940)]
We should do the same for the issues, but, yeah, we're..

##### **Chenyu** [[00:32:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1942)]
No, so the issues, I went through that multiple times, and many times things are still broken.

##### **Nimlgen** [[00:32:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1952)]
Wait, so we really have 127 issues still?

##### **Qazalin** [[00:32:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1956)]
I mean, probably like 20% of them might not be relevant or not true anymore, but a lot

##### **Geohot** [[00:32:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1963)]
of the issue is true.

##### **Geohot** [[00:32:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1965)]
I see.

##### **Geohot** [[00:32:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1966)]
Yeah.

##### **Qazalin** [[00:32:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1967)]
So, yeah, we can start fixing issues.

##### **Chenyu** [[00:32:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1969)]
I mean, hopefully we're kind of in a place where it's..

##### **Nimlgen** [[00:32:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1973)]
I don't know.

##### **Qazalin** [[00:32:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1974)]
I just feel that the deletion of Shape Tracker and the deletion of kernel.py puts us in a

##### **Geohot** [[00:32:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1979)]
place where there's not much more to delete, so we can start actually fixing issues.

##### **Geohot** [[00:33:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1986)]
It's not like, oh, it's going to be fixed in the next rewrite.

##### **Geohot** [[00:33:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1988)]
The only big rewrite I kind of see incoming is going to be things that, yeah, again, if

##### **Qazalin** [[00:33:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1995)]
we find ourselves tweaking symbolic..

##### **Chenyu** [[00:33:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1997)]
The rule order?

##### **Nimlgen** [[00:33:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=1998)]
That's just going to all be fixed with egraphs.

##### **Qazalin** [[00:33:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2003)]
Or anything that effectively looks like, oh, like, we had to write this one rule to combine

##### **Geohot** [[00:33:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2009)]
these three rules because it doesn't match, right?

##### **Geohot** [[00:33:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2012)]
Like, this is all going to go away with egraphs.

##### **Geohot** [[00:33:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2014)]
We have to do it.

##### **Qazalin** [[00:33:35](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2015)]
I mean, there's no way.

##### **Chenyu** [[00:33:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2016)]
Because, like, some guy posted, oh, there was an issue..

##### **Nimlgen** [[00:33:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2021)]
There was an issue where someone thought, like, two things should be equal.

##### **Qazalin** [[00:33:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2024)]
Here, the expression equality bug.

##### **Geohot** [[00:33:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2028)]
And, like, we need to fix this.

##### **Geohot** [[00:33:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2034)]
Like, there's those two expressions.

##### **Geohot** [[00:33:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2035)]
Isn't that one just the person didn't co-simplify?

##### **Qazalin** [[00:33:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2039)]
No.

##### **Chenyu** [[00:34:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2040)]
Well, part of the problem is they used equals equals and not not equals, which is fine.

##### **Nimlgen** [[00:34:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2044)]
They were using it wrong.

##### **Qazalin** [[00:34:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2045)]
But even if you use it right, it's still wrong.

##### **Geohot** [[00:34:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2047)]
It still doesn't work.

##### **Geohot** [[00:34:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2056)]
Like, because it had a..

##### **Geohot** [[00:34:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2057)]
We have to fix this.

##### **Qazalin** [[00:34:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2057)]
Yeah.

##### **Chenyu** [[00:34:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2057)]
We don't have a lot of leaves.

##### **Nimlgen** [[00:34:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2060)]
I don't think egraph can solve that.

##### **Qazalin** [[00:34:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2062)]
I don't know.

##### **Geohot** [[00:34:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2063)]
No, egraph can totally..

##### **Geohot** [[00:34:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2065)]
But polynomial canonicalization is a pretty hard problem.

##### **Geohot** [[00:34:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2069)]
What do you mean?

##### **Qazalin** [[00:34:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2070)]
But egraph can totally solve it.

##### **Chenyu** [[00:34:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2072)]
But this is trivial for egraph to solve.

##### **Nimlgen** [[00:34:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2077)]
It's a pretty hard problem.

##### **Qazalin** [[00:34:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2081)]
Well, you don't solve it, but the egraph doesn't solve it with canonicalization.

##### **Geohot** [[00:34:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2086)]
Uh..

##### **Geohot** [[00:34:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2087)]
Yeah.

##### **Geohot** [[00:34:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2091)]
It's like a union finds them, right?

##### **Qazalin** [[00:34:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2092)]
Yeah.

##### **Chenyu** [[00:34:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2093)]
They just have the same representative.

##### **Nimlgen** [[00:34:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2094)]
Yeah, yeah, yeah.

##### **Qazalin** [[00:34:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2095)]
And if the two..

##### **Geohot** [[00:34:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2096)]
And the egraph would do explicitly the look for equality.

##### **Geohot** [[00:35:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2106)]
But also, why is polynomial..

##### **Geohot** [[00:35:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2109)]
Why is this a hard problem?

##### **Qazalin** [[00:35:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2113)]
Oh, it's just very hard.

##### **Chenyu** [[00:35:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2114)]
Just imagine every variable you can have, how you add a sign to it, and you start trying

##### **Nimlgen** [[00:35:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2121)]
to solve weird polynomial.

##### **Qazalin** [[00:35:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2127)]
Anyway.

##### **Geohot** [[00:35:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2129)]
Yeah.

##### **Geohot** [[00:35:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2130)]
I mean..

##### **Geohot** [[00:35:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2131)]
So, the most generic form, it's a very hard problem.

##### **Qazalin** [[00:35:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2137)]
We probably don't need that.

##### **Chenyu** [[00:35:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2139)]
But then we are..

##### **Nimlgen** [[00:35:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2140)]
Yeah.

##### **Qazalin** [[00:35:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2140)]
We started to discuss, like, what do we use?

##### **Geohot** [[00:35:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2143)]
Then we kind of..

##### **Geohot** [[00:35:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2144)]
We kind of settled previously on what's the real kernel that we encounter.

##### **Geohot** [[00:35:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2148)]
And that's why we don't have all of these equality things expressed in rewriting rules.

##### **Qazalin** [[00:35:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2153)]
Yeah.

##### **Chenyu** [[00:35:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2156)]
I don't know.

##### **Nimlgen** [[00:35:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2156)]
I mean, I know things like this are very easy in egraphs.

##### **Qazalin** [[00:35:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2159)]
I'm not sure it's so easy to say that there's, like, a desirable canonical form.

##### **Geohot** [[00:36:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2164)]
Yeah.

##### **Geohot** [[00:36:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2164)]
Because previously..

##### **Geohot** [[00:36:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2165)]
We probably still use this in somewhere that we use this to find those strides for stuff,

##### **Qazalin** [[00:36:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2171)]
especially when your coefficient can be another variable.

##### **Chenyu** [[00:36:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2174)]
Yeah.

##### **Nimlgen** [[00:36:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2175)]
I mean, that's not a polynomial anymore, right?

##### **Qazalin** [[00:36:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2179)]
I mean, it's still a polynomial.

##### **Geohot** [[00:36:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2182)]
If your coefficient can be a variable?

##### **Geohot** [[00:36:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2184)]
Yeah.

##### **Geohot** [[00:36:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2185)]
Your coefficient is a variable, but it's, like, a variable from your shape and not your

##### **Qazalin** [[00:36:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2190)]
variable in your polynomial.

##### **Chenyu** [[00:36:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2192)]
Then in this case, do you rewrite or not?

##### **Nimlgen** [[00:36:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2194)]
How can rewriting rules tell if you should flip these two or not?

##### **Qazalin** [[00:36:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2198)]
Yeah.

##### **Geohot** [[00:36:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2198)]
Yeah.

##### **Geohot** [[00:36:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2199)]
No.

##### **Geohot** [[00:36:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2199)]
Of course.

##### **Qazalin** [[00:36:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2199)]
Yeah.

##### **Chenyu** [[00:36:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2199)]
You can't.

##### **Nimlgen** [[00:36:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2200)]
You can't do that.

##### **Qazalin** [[00:36:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2201)]
That's where we started to get, like, do we include these flattening rules or not?

##### **Geohot** [[00:36:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2205)]
Do we sort this or not?

##### **Geohot** [[00:36:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2208)]
That thing is no longer a polynomial, right?

##### **Geohot** [[00:36:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2212)]
What do you mean?

##### **Qazalin** [[00:36:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2212)]
It's still a polynomial.

##### **Chenyu** [[00:36:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2213)]
It's linear.

##### **Nimlgen** [[00:36:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2214)]
It's a linear function.

##### **Qazalin** [[00:36:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2217)]
It's not a linear function.

##### **Geohot** [[00:36:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2218)]
I'm multiplying a variable by another variable.

##### **Geohot** [[00:37:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2220)]
Yeah.

##### **Geohot** [[00:37:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2221)]
But in this context, you treat one variable as a constant.

##### **Qazalin** [[00:37:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2224)]
That's fixed when you do something.

##### **Chenyu** [[00:37:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2225)]
Yeah.

##### **Nimlgen** [[00:37:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2225)]
But you can't..

##### **Qazalin** [[00:37:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2227)]
Anyway.

##### **Geohot** [[00:37:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2229)]
Yeah.

##### **Geohot** [[00:37:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2231)]
I think these..

##### **Geohot** [[00:37:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2236)]
I don't know.

##### **Qazalin** [[00:37:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2237)]
I guess we would know if we really start to include eGraph.

##### **Chenyu** [[00:37:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2241)]
We probably would know better.

##### **Nimlgen** [[00:37:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2244)]
Yeah.

##### **Qazalin** [[00:37:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2244)]
I don't know.

##### **Geohot** [[00:37:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2246)]
I'll just scan this week and then maybe next week I'll start looking into eGraph.

##### **Geohot** [[00:37:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2250)]
I mean, it's something we have to do.

##### **Geohot** [[00:37:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2251)]
But it also..

##### **Qazalin** [[00:37:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2252)]
It's very nice how I think we can very, like, comfortably transition to it.

##### **Chenyu** [[00:37:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2257)]
There's going to be no..

##### **Nimlgen** [[00:37:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2258)]
It's all the same rewriting.

##### **Qazalin** [[00:37:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2259)]
Yeah, I mean, like, in the past, if you've done a lot of rewriting, you've done..

##### **Geohot** [[00:37:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2260)]
So, to go back to the old, like, string of rules, it just sometimes applies them

##### **Geohot** [[00:37:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2262)]
more.

##### **Geohot** [[00:37:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2262)]
And instead of giving you one output graph, it gives you a data structure which contains

##### **Qazalin** [[00:37:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2266)]
millions.

##### **Chenyu** [[00:37:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2268)]
Oh, sounds good.

##### **Nimlgen** [[00:37:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2271)]
Okay.

##### **Qazalin** [[00:37:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2275)]
I think Losberts lock the GPT-OSS.

##### **Geohot** [[00:38:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2280)]
Is that true?

##### **Geohot** [[00:38:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2283)]
Oh, yeah.

##### **Geohot** [[00:38:04](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2284)]
We can lock..

##### **Qazalin** [[00:38:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2285)]
GPT..

##### **Chenyu** [[00:38:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2286)]
What's the current speed on GPT-OSS?

##### **Nimlgen** [[00:38:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2293)]
I have no idea.

##### **Qazalin** [[00:38:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2294)]
Is he wrong?

##### **Geohot** [[00:38:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2295)]
I think it runs, but I think it's just that the speed isn't good.

##### **Geohot** [[00:38:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2300)]
And like how far we..

##### **Geohot** [[00:38:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2302)]
0.1 tokens per second.

##### **Qazalin** [[00:38:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2304)]
Okay, we're 1,000x off.

##### **Chenyu** [[00:38:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2305)]
All right.

##### **Nimlgen** [[00:38:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2305)]
All right.

##### **Qazalin** [[00:38:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2307)]
That's something.

##### **Geohot** [[00:38:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2312)]
All right.

##### **Geohot** [[00:38:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2312)]
I'll relock the torch back end based on that picture.

##### **Geohot** [[00:38:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2316)]
But yeah, no, we do need it to not..

##### **Qazalin** [[00:38:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2323)]
If it's realizing at every torch thing, there's no point.

##### **Chenyu** [[00:38:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2326)]
It's got to still be kind of lazy.

##### **Nimlgen** [[00:38:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2335)]
So let's GPT OSs.

##### **Qazalin** [[00:39:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2340)]
Then we have this torch back end lock.

##### **Geohot** [[00:39:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2346)]
GPT OSs also locked.

##### **Geohot** [[00:39:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2352)]
Yeah, I'll lock GPT OSs, but why is the speed so bad?

##### **Geohot** [[00:39:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2376)]
Not sure why it's so slow.

##### **Qazalin** [[00:39:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2377)]
Okay.

##### **Chenyu** [[00:39:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2390)]
I would pay out that bounty about proportional to the speed.

##### **Nimlgen** [[00:39:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2395)]
So if at the end you get to 50 tokens per second, half the bounty.

##### **Qazalin** [[00:40:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2400)]
At 0.1 tokens per second, it's worth a dollar.

##### **Geohot** [[00:40:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2403)]
Okay.

##### **Geohot** [[00:40:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2414)]
Cool.

##### **Geohot** [[00:40:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2420)]
I think there are supposed to updates on the whisper.

##### **Qazalin** [[00:40:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2429)]
I mean, there's always constant updates on

##### **Chenyu** [[00:40:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2431)]
the whisper.

##### **Nimlgen** [[00:40:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2431)]
I don't know.

##### **Qazalin** [[00:40:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2432)]
We just have to put something up that you want me to merge.

##### **Geohot** [[00:40:36](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2436)]
I don't need every update on this.

##### **Geohot** [[00:40:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2439)]
Oh, this is good. I want to merge it. Okay, cool.

##### **Geohot** [[00:40:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2451)]
We're going to do HVAC, so I'll lock that one.

##### **Qazalin** [[00:40:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2459)]
Oh, USB 3.0. Don't believe we have a bounty for that.

##### **Chenyu** [[00:41:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2465)]
These bounties still look good.

##### **Nimlgen** [[00:41:08](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2468)]
Oh, I'm deleting the HLBC far torch bounty one.

##### **Qazalin** [[00:41:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2471)]
All I get is LLM crap for that.

##### **Geohot** [[00:41:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2474)]
Same thing with the Beautiful MNIST.

##### **Geohot** [[00:41:17](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2477)]
Oh, no. The Beautiful MNIST torch one I'll leave,

##### **Geohot** [[00:41:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2479)]
because LLMs can't do that one.

##### **Qazalin** [[00:41:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2481)]
LLMs just misunderstand that one.

##### **Chenyu** [[00:41:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2483)]
The CIFAR one they understand, and they give me something that's..

##### **Nimlgen** [[00:41:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2486)]
Just a reminder, I don't care if you use AI,

##### **Qazalin** [[00:41:31](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2491)]
but if you copy and paste from the AI

##### **Geohot** [[00:41:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2494)]
something that you do not understand,

##### **Geohot** [[00:41:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2497)]
you are wasting my time.

##### **Geohot** [[00:41:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2499)]
And I think that we might start doing just GitHub bans if people do that.

##### **Qazalin** [[00:41:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2503)]
Don't do that. Don't do that. Please don't do that.

##### **Chenyu** [[00:41:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2506)]
You want to use AI? Use AI. It's great. I use AI. Everyone loves AI.

##### **Nimlgen** [[00:41:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2509)]
But if you're just copying and pasting something you don't understand,

##### **Qazalin** [[00:41:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2512)]
you're actually more..

##### **Geohot** [[00:41:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2513)]
You're more useless than the AI.

##### **Geohot** [[00:41:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2515)]
I can do that too.

##### **Geohot** [[00:41:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2516)]
I can also copy and paste things I don't understand from the AI.

##### **Qazalin** [[00:41:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2519)]
What did you do here?

##### **Chenyu** [[00:42:00](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2520)]
The point of people is to look at the AI and be like,

##### **Nimlgen** [[00:42:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2523)]
wow, this thing's hallucinating garbage,

##### **Qazalin** [[00:42:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2525)]
which about half the time it is.

##### **Geohot** [[00:42:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2535)]
But it was a lot of fun vibe reversing SQTT.

##### **Geohot** [[00:42:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2538)]
GPT 5.1 is pretty good.

##### **Geohot** [[00:42:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2542)]
It's the best reverse.

##### **Qazalin** [[00:42:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2543)]
It's the best engineer I've seen in a model.

##### **Chenyu** [[00:42:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2547)]
Yeah, I think LLM is really good working on like translation or anything.

##### **Nimlgen** [[00:42:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2553)]
Anytime you already have every context you need in your input prompt.

##### **Qazalin** [[00:42:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2558)]
Yeah, I mean, I can literally copy and paste the decompiled stuff from

##### **Geohot** [[00:42:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2562)]
Ghidra into the LLM and be like, what does this do?

##### **Geohot** [[00:42:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2565)]
And like, it would take me 30 minutes to read the function and the LLM

##### **Geohot** [[00:42:48](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2568)]
gives me an answer in two minutes.

##### **Qazalin** [[00:42:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2569)]
So it's great.

##### **Chenyu** [[00:42:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2570)]
That's pretty good.

##### **Nimlgen** [[00:42:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2572)]
But yeah, yeah.

##### **Qazalin** [[00:42:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2573)]
It's translation.

##### **Geohot** [[00:42:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2573)]
Basically, that's why it's good.

##### **Geohot** [[00:42:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2576)]
Yeah, cool.

##### **Geohot** [[00:42:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2579)]
Yeah, I think the yeah, the HVAC decode thing is quite important to us.

##### **Qazalin** [[00:43:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2586)]
Comm is not using a whole bunch of their GPUs because their current HVAC decoder

##### **Chenyu** [[00:43:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2592)]
uses tons of memory.

##### **Nimlgen** [[00:43:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2596)]
So hopefully we can get to the bottom of that and not use all the memory.

##### **Qazalin** [[00:43:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2604)]
Yeah, no more.

##### **Geohot** [[00:43:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2605)]
Yeah, no more.

##### **Geohot** [[00:43:25](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2605)]
Jen, anything we can do to make that easier?

##### **Geohot** [[00:43:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2610)]
No, I think.

##### **Qazalin** [[00:43:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2617)]
Cool.

##### **Chenyu** [[00:43:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2619)]
Oh, there's still a bug also in timing with PM for today.

##### **Nimlgen** [[00:43:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2625)]
You fixed it.

##### **Qazalin** [[00:43:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2626)]
Wait, you know, this was happening yesterday.

##### **Geohot** [[00:43:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2630)]
Yeah, I fix it today.

##### **Geohot** [[00:43:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2632)]
Today.

##### **Geohot** [[00:43:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2633)]
Today.

##### **Qazalin** [[00:43:53](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2633)]
OK, cool.

##### **Chenyu** [[00:43:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2634)]
Oh, here.

##### **Nimlgen** [[00:43:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2635)]
AMD time effects.

##### **Qazalin** [[00:43:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2636)]
What was it?

##### **Geohot** [[00:43:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2638)]
And it's pretty.

##### **Geohot** [[00:44:01](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2641)]
I just read Mesa in details and they just actually, they actually have like two.

##### **Geohot** [[00:44:12](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2652)]
Like they call release mem twice?

##### **Qazalin** [[00:44:15](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2655)]
Yeah, because actually, I know I can't reproduce this on RDA3.

##### **Chenyu** [[00:44:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2662)]
Yeah.

##### **Nimlgen** [[00:44:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2663)]
But I think it's only on RDA4.

##### **Qazalin** [[00:44:27](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2667)]
But yeah, it's.

##### **Geohot** [[00:44:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2670)]
But actually on RDA, they think that the full flash of after compute shader is to use the

##### **Geohot** [[00:44:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2678)]
event right.

##### **Geohot** [[00:44:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2679)]
We do like in the exec and the release mem.

##### **Qazalin** [[00:44:45](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2685)]
So not the timer one.

##### **Chenyu** [[00:44:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2687)]
So I think that was the problem.

##### **Nimlgen** [[00:44:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2690)]
I see.

##### **Qazalin** [[00:44:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2691)]
Yeah, no, I mean, I see how there's two.

##### **Geohot** [[00:44:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2692)]
Release mems in the in the signal.

##### **Geohot** [[00:44:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2696)]
Cool.

##### **Geohot** [[00:44:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2698)]
I mean, yeah, I shouldn't be too soft.

##### **Qazalin** [[00:44:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2699)]
Should be fine.

##### **Chenyu** [[00:45:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2705)]
I don't know.

##### **Nimlgen** [[00:45:05](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2705)]
Those names have always been weird to me.

##### **Qazalin** [[00:45:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2707)]
Release mem and acquire mem.

##### **Geohot** [[00:45:09](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2709)]
Do they make sense to you?

##### **Geohot** [[00:45:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2713)]
Yeah.

##### **Geohot** [[00:45:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2714)]
I mean, it's kind of like atomic ordering.

##### **Qazalin** [[00:45:18](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2718)]
It's the same things.

##### **Chenyu** [[00:45:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2720)]
Yeah, but what is what is acquire mem do?

##### **Nimlgen** [[00:45:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2724)]
So actually, like, it won't allow any packets reorder.

##### **Qazalin** [[00:45:34](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2734)]
Like, which have button like it's basically when you take log, you have to function to

##### **Geohot** [[00:45:40](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2740)]
acquire mem and to release mem.

##### **Geohot** [[00:45:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2742)]
Sure.

##### **Geohot** [[00:45:43](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2743)]
And you're not allowed to like to cross these boundaries.

##### **Qazalin** [[00:45:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2749)]
I mean, if you release mem.

##### **Chenyu** [[00:45:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2751)]
Yeah.

##### **Nimlgen** [[00:45:51](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2751)]
Yeah.

##### **Qazalin** [[00:45:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2752)]
All the upper instructions have been.

##### **Geohot** [[00:45:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2757)]
Sure.

##### **Geohot** [[00:45:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2758)]
Sure.

##### **Geohot** [[00:45:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2758)]
Okay.

##### **Qazalin** [[00:45:58](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2758)]
That makes sense to me.

##### **Chenyu** [[00:45:59](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2759)]
Like acquire mem is like acquiring a lock on the memory.

##### **Nimlgen** [[00:46:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2763)]
Yeah, it's a fence with acquire semantics, right?

##### **Qazalin** [[00:46:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2766)]
That's what the choir cement.

##### **Geohot** [[00:46:07](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2767)]
Isn't that like a thing that people talk about with?

##### **Geohot** [[00:46:10](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2770)]
I believe it.

##### **Geohot** [[00:46:11](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2771)]
Okay.

##### **Qazalin** [[00:46:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2773)]
Um, but okay.

##### **Chenyu** [[00:46:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2774)]
All right, good.

##### **Nimlgen** [[00:46:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2774)]
That that that's a simple way to think about it.

##### **Qazalin** [[00:46:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2776)]
I mean, it's just weird to me that you have to do to release mems.

##### **Geohot** [[00:46:19](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2779)]
But if it works and Mesa does that, then yeah.

##### **Geohot** [[00:46:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2782)]
Yeah.

##### **Geohot** [[00:46:23](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2783)]
Yeah, because I think the timer one is a fake one.

##### **Qazalin** [[00:46:26](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2786)]
Kind of.

##### **Chenyu** [[00:46:28](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2788)]
Oh, I see.

##### **Nimlgen** [[00:46:29](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2789)]
So you're saying that it's not actually doing it if you're doing the timer, right?

##### **Qazalin** [[00:46:33](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2793)]
It's not actually doing the normal release.

##### **Geohot** [[00:46:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2797)]
Okay, acquire it.

##### **Geohot** [[00:46:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2798)]
That's what you're saying.

##### **Geohot** [[00:46:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2799)]
Yeah.

##### **Qazalin** [[00:46:39](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2799)]
I'm thinking back to operating systems class and it's like a semaphore.

##### **Chenyu** [[00:46:42](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2802)]
You want to acquire the mutex while you don't want this.

##### **Nimlgen** [[00:46:46](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2806)]
That's like a

##### **Qazalin** [[00:46:47](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2807)]
because it's not a lot because you don't you never release it.

##### **Geohot** [[00:46:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2809)]
So you'd be like, right.

##### **Geohot** [[00:46:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2810)]
You'd be.

##### **Geohot** [[00:46:50](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2810)]
Yeah.

##### **Qazalin** [[00:46:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2812)]
Yeah.

##### **Chenyu** [[00:47:03](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2823)]
I think that's it for the schedule agenda.

##### **Nimlgen** [[00:47:06](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2826)]
Anything else?

##### **Qazalin** [[00:47:13](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2833)]
Oh, yeah.

##### **Geohot** [[00:47:14](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2834)]
End of the end of the year.

##### **Geohot** [[00:47:16](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2836)]
We're going to be training LLaMA.

##### **Geohot** [[00:47:20](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2840)]
8B.

##### **Qazalin** [[00:47:21](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2841)]
We're going to have a lot of 405.

##### **Chenyu** [[00:47:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2842)]
Yeah.

##### **Nimlgen** [[00:47:22](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2842)]
We're going to have a lot of 45B that starts up fast.

##### **Qazalin** [[00:47:24](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2844)]
And we're going to have decent GEMM and flash retention kernels written in UOPs running

##### **Geohot** [[00:47:30](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2850)]
for the LLaMA 8B.

##### **Geohot** [[00:47:32](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2852)]
And then just next year, we got to we got to scale it up, debug a bunch of issues.

##### **Geohot** [[00:47:37](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2857)]
And we should be good.

##### **Qazalin** [[00:47:38](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2858)]
But yeah, I know if we can get it, we can get an 8B training by the end of the year.

##### **Chenyu** [[00:47:41](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2861)]
We're so on track.

##### **Nimlgen** [[00:47:44](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2864)]
Especially if we can do it with scan and stuff.

##### **Qazalin** [[00:47:49](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2869)]
Good.

##### **Geohot** [[00:47:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2872)]
Cool.

##### **Geohot** [[00:47:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2872)]
Yeah.

##### **Geohot** [[00:47:52](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2872)]
Great.

##### **Qazalin** [[00:47:54](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2874)]
Thanks, everyone.

##### **Chenyu** [[00:47:55](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2875)]
Thanks for this meeting.

##### **Nimlgen** [[00:47:56](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2876)]
Thanks, everyone.

##### **Qazalin** [[00:47:57](https://www.youtube.com/watch?v=cLnu8McQRlw&t=2877)]
Bye bye.
