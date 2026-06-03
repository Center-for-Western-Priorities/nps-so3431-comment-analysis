import re
import pandas as pd

df = pd.read_excel('/mnt/user-data/uploads/NPS_SO3431_QR_Comments-For-Release.xlsx')
FEEDBACK_COL = 'Your feedback:'
PARK_COL = 'Which park is your feedback about?'

# ── Pass 1: Template detection ────────────────────────────────────────────────

def detect_template(text):
    if pd.isna(text): return 'empty'
    t = str(text)
    if t.strip().startswith('RE: Jan 6th'): return 'template_jan6'
    if re.match(r'^National Parks (are|generate|protect|preserve|safeguard|inspire|provide|serve|support|create|offer|represent|remain|connect|encourage|foster|help|stand|build|remind|attract)', t.strip()): return 'template_nps_facts'
    if re.match(r'^(A diverse|Diversity in|Exposure to|Immigrant|Immigration|Immigrants)', t.strip()) and len(t.strip()) < 150: return 'template_diversity_facts'
    if 'To local NPS employees' in t and 'unconscionable attack' in t: return 'template_nps_solidarity'
    if "I'm writing to express my disgust, shock" in t: return 'template_disgust'
    if len(t.strip()) < 40 and '8647' in t: return 'template_8647_only'
    if 'America loves the NPS' in t and len(t.strip()) < 80: return 'template_america_loves'
    if "It's a park ranger's job to interpret history in a factual" in t: return 'template_ranger_job'
    if 'I am writing not as a lobbyist or a politician, but as an American father' in t: return 'template_father'
    if 'I am writing as an American mother, grandmother, artist and teacher' in t: return 'template_mother'
    if re.match(r'^(The Cybersecurity|Pre-election testing|Recounts and audits|Audits in multiple)', t.strip()): return 'template_election_facts'
    if re.match(r'^Restore truth by restoring references to (trans|tans) people on the Stonewall', t.strip()): return 'template_stonewall_trans'
    return None

# ── Pass 2: Original comment classification (v3) ──────────────────────────────
#
# KEY DISTINCTION (from human review):
#
# DEFEND HISTORY: Comment explicitly discusses the importance of accurate,
#   complete, or honest history — the BULK of the comment is about history
#   itself: what it means, why it matters, what should/shouldn't be in parks.
#   The historical argument is the primary content.
#
# GENERAL OPPOSITION: Comment opposes the order, the QR sign, or the
#   administration's direction WITHOUT making history the primary focus.
#   "This sign is offensive," "take down the snitch signs," "this order
#   is unAmerican" — reaction to the policy mechanism rather than a
#   substantive argument about history.
#
# If a comment does both, lean toward DEFEND HISTORY if the historical
#   argument is substantive and takes up most of the text.
#   Lean toward GENERAL OPPOSITION if the historical reference is brief
#   or incidental ("we can't erase history!" as a one-liner).
#
# FLAGGED: Only comments criticizing a specific pre-existing interpretive
#   sign or exhibit — NOT the QR code sign itself. The QR code / snitch
#   sign is the mechanism; interpretive signs are the content under review.
#
# TRUMP/BURGUM: Personal attacks on named individuals. Policy opposition
#   that names them is general opposition. "Hands off our history" is
#   general opposition even if it names Trump.
#
# PARK VISIT: Physical visit experience only — facilities, trails, ranger
#   performance, accessibility. If the comment also addresses the order
#   or history, it's not park visit experience.

# ── Compiled patterns ─────────────────────────────────────────────────────────

# Signals that the QR code / snitch sign / EO is being discussed
QR_SIGN = re.compile(
    r'(snitch sign|snitch form|tattletale sign|qr code sign|'
    r'eo\s*14253|executive order 14253|secretary order 3431|so\s*3431|'
    r'sign (ask|request|tell|instruct|requir).{0,50}(report|negative|disparag)|'
    r'(report|flag).{0,40}(negative|disparag).{0,40}(sign|american|histor)|'
    r'negative about (past|living|either) (past |living |either )?americans|'
    r'fail to emphasize the beauty.{0,30}grandeur|'
    r'restoring truth and sanity|'
    r'this sign is (offensive|negative|unamerican|wrong|absurd|ridiculous|disgusting|insulting|repuls|appalling|outrageous|disgraceful)|'
    r'(the |this |that |a )sign.{0,40}(is|was|are|were).{0,30}(offensive|negative|unamerican|wrong|absurd|ridiculous|disgusting|insulting|appalling|outrageous|disgraceful|troubling|disturbing|alarming|concerning|foolish|idiotic|stupid)|'
    r'sign (asking|request|instruct|tell).{0,30}(report|snitch|flag|narc|tattle)|'
    r'(awful|offensive|disgusting|absurd|outrageous|ridiculous|insulting|appalling|repulsive|foolish|idiotic).{0,40}sign|'
    r'(remove|take down|get rid of|tear down).{0,30}(this sign|the sign|snitch|qr|these signs)|'
    r'the sign.{0,60}(should be removed|needs to go|must go|take it down|come down)|'
    r'signs (should|must|need to).{0,20}(go|come down|be removed|be taken down))',
    re.IGNORECASE
)

# Detects comments quoting the QR code sign text rather than reporting an exhibit
QR_QUOTE = re.compile(
    r'(any signs or other information that are negative about|'
    r'negative about either past or living|'
    r'fail to emphasize the beauty.{0,20}grandeur)',
    re.IGNORECASE
)


# Signals that HISTORY is the primary subject — the argument is substantive
# about what history means, what belongs in parks, why accuracy matters
HISTORY_PRIMARY = re.compile(
    r'('
    # Explicit arguments about historical accuracy/completeness
    r'(full|complete|honest|accurate|true|factual|unbiased|real|objective).{0,40}(american )?histor(y|ical)|'
    r'histor(y|ical).{0,40}(must|should|needs to|cannot|can.t|ought).{0,40}(be )?(complete|honest|accurate|told|preserved|protect|censor|eras|rewrit|sanitiz|scrub|alter|chang|remov|suppress|whitewash|hide)|'
    r'(whitewash|censor|eras|rewrite|sanitize|scrub|suppress|alter|distort|falsif).{0,40}(histor|past|truth|record)|'
    r'(painful|dark|ugly|uncomfortable|difficult|complex|complicated|shameful|difficult).{0,50}histor.{0,70}(import|must|should|learn|tell|told|preserv|acknowledg|face|confront|reckon|understand)|'
    r'learn from (our |the )?(mistake|past|histor|wrong)|'
    r'(those who (don.t|do not|forget|ignore|fail to learn).{0,20}(histor|past)).{0,30}(repeat|doom)|'
    r'(doomed to repeat|repeat.{0,10}mistake).{0,30}(histor|past)|'
    r'histor(y|ical) (is|includes|encompasses|covers|contains).{0,50}(good and bad|both|triumph|tragedy|complex|conflict|all|positive and negative)|'
    r'(leave|let).{0,20}histor.{0,20}(to )?(historian|expert|scholar|professional|ranger)|'
    # Arguments about specific historical content that belongs in parks
    r'(accurate|factual|honest|truthful|unbiased|complete).{0,40}(interpret|exhibit|sign|display|portrayal|presentation|account|depiction)|'
    r'(erasure|erasing|removing|deleting|censoring).{0,40}(histor|past|truth|record|exhibit|sign)|'
    r'(climate change|glacier|sea level|global warming).{0,60}(sign|exhibit|information|accurate|science|true|real|fact)|'
    r'(native|indigenous|tribal).{0,80}histor.{0,40}(belong|import|must|should|told|preserv|includ|acknowledg)|'
    r'(enslaved|slavery|japanese american|incarceration|internment|civil rights|lgbtq|stonewall|manzanar|civil war|genocide|massacre|segregation).{0,80}(histor|must|should|told|preserv|acknowledg|cannot|not).{0,30}(remov|eras|censor|tak|delet|chang|alter|forget|ignor|suppress|whitewash)|'
    r'(restore|preserve|protect|maintain|keep).{0,40}(histor|interpret|exhibit|accurate|complete|honest)|'
    r'(orwellian|1984|newspeak|memory.?hole|thought.?polic|big brother).{0,50}(histor|censor|eras|rewrite|park|truth)|'
    r'history (repeats|will repeat|has a way of repeating)|'
    # The QR sign framed as anti-historical (history is still the subject)
    r'(this sign|the sign|snitch sign|these signs).{0,100}(whitewash|censor|eras|rewrite|sanitize|anti.?histor|anti.?american histor|history)|'
    r'(whitewash|censor|eras|sanitize|rewrite).{0,40}(history|past|truth).{0,100}(sign|order|eo|administration)'
    r'|(value|importance|sharing).{0,20}(all elements of|all parts of|all aspects of).{0,20}(our )?history'
    r'|(good and bad|good or bad).{0,30}(history|past|american)'
    r'|(faithful slave|United Daughters of Confederacy|UDC).{0,60}(monument|sign|plaque|marker)'
    r'|(historians?.{0,10}(of the last|over the past|from the last).{0,10}\d+ (plus )?years?)'
    r')',
    re.IGNORECASE
)

# Pro-removal: visitor actually wants signs removed / agrees with EO
PRO_REMOVAL = re.compile(
    r'(too woke|woke sign|woke agenda|woke content|woke (park|nps)|'
    r'one.?sided (history|narrative|portrayal|content)|'
    r'biased (sign|exhibit|content|portrayal)|'
    r'anti.?american (sign|exhibit|content|narrative|portrayal)|'
    r'partisan (sign|agenda|content|exhibit)|'
    r'far.?left.{0,20}(sign|park|content|exhibit)|'
    r'executive order.{0,30}(correct|right|proper|good|support|agree)|'
    r'14253.{0,30}(right|correct|good|support|proper|agree)|'
    r'refusal to make changes required by.{0,30}executive order|'
    r'second complaint.{0,30}refusal to make changes|'
    r'not in accordance with executive order 14253|'
    r'wall of fame.{0,30}negative.{0,30}executive order|'
    r'(disparag|disparage).{0,40}(american|president|living|past).{0,20}(should|must|need).{0,20}(remov|tak|delet|chang))',
    re.IGNORECASE
)

# True interpretive sign criticism (not about the QR sign)
INTERPRETIVE_SIGN_CRIT = re.compile(
    r'('
    # Criticism of specific pre-existing sign/exhibit content
    r'(sign|exhibit|placard|display|panel|marker|monument|plaque|mural|wayside).{0,100}'
    r'(should be removed|should be taken down|should be changed|should not be there|'
    r'is wrong|is incorrect|is inaccurate|is biased|is one.?sided|'
    r'disparages|is disparaging|is inappropriate|does not reflect|misrepresent|'
    r'negative portrayal|too negative|one.?sided|should not say)|'
    # Requesting restoration of specific removed content at a named park/site
    r'restore truth by restoring (references|information|content|exhibits?|signs?).{0,60}'
    r'(to |on |at |in )(the |this |our )?(stonewall|park|monument|memorial|site|museum)|'
    # Quoting specific wall/exhibit text as problematic (must name the physical object)
    r'(the )?(words|text|language|wording) on the (wall|sign|plaque|panel|exhibit|display)'
    r'.{0,80}(negative|wrong|inaccurate|inappropriate|disparag|offensive|mislead)|'
    # Signage is missing specific group information (requesting more content)
    r'(signage|sign|exhibit|display).{0,30}(doesn.t|does not|lack|missing|absent).{0,30}'
    r'(information|content|representation).{0,30}'
    r'(native|indigenous|tribal|enslaved|slavery|lgbtq|trans|climate|glacier|specific group)'
    r')',
    re.IGNORECASE
)

# Facility-only: physical park experience with no political content
FACILITY = re.compile(
    r'(elevator|bathroom|restroom|toilet|parking (lot|space|fee|pass)|'
    r'trail (is|was) (closed|damaged|overgrown|blocked|washed out|eroded)|'
    r'shower.{0,20}(mold|broken|dirty|hot water|cold water)|'
    r'faucet|broken (fence|gate|bench|railing|bridge|equipment|fixture)|'
    r'reservation system|vehicle reservation|timed entry permit|'
    r'campground (full|overbooked|flooded|damaged|noisy|dirty)|campsite|'
    r'visitor center (is|was) (closed|locked|unstaffed|not open)|'
    r'porta.?potty|pit toilet|composting toilet|'
    r'cell (service|reception|signal) (is|was) (poor|bad|nonexistent|terrible)|'
    r'entrance fee|day.use fee|too expensive|not worth the fee|cost too much|'
    r'picnic table (is|was|are|were) (broken|damaged|dirty|missing)|'
    r'speed limit|road (is|was) (closed|damaged|washed out|flooded|unpaved)|'
    r'ADA|wheelchair|accessibility|accessible|handicap)',
    re.IGNORECASE
)

POLITICAL = re.compile(
    r'(trump|burgum|doge|maga|administration|executive order|whitewash|'
    r'erase history|censor|snitch|public lands|indigenous|'
    r'climate change|civil rights|slavery|native american|sell off)',
    re.IGNORECASE
)

# Pure personal attacks on named individuals
PERSONAL_ATTACK = re.compile(
    r'trump.{0,30}(tiny|small|baby).{0,10}hand'
    r'|(tiny|small|baby).{0,10}hand.{0,20}trump'
    r'|trump.{0,30}(hair|wig|combover|toupee)'
    r'|trump.{0,30}(orange|tan|spray tan|bronzer)'
    r'|trump.{0,30}(stupid|idiot|dumb|moron|buffoon|clown|loser|coward|liar|cheat|fraud|criminal|felon|pervert|creep|pig|fool|embarrassment)'
    r'|trump.{0,30}(not a combover|national security threat)'
    r'|(not a combover|national security threat).{0,30}trump'
    r'|trump (signs|wrote|signed).{0,30}(crayon|sharpie|big|small|tiny)'
    r'|(burgum|bergum|hegseth|bannon|miller).{0,30}(idiot|moron|awful|terrible|disgusting|evil|corrupt|criminal|paws|greasy|fool|disgrace|disaster|incompetent|ruining|destroying)'
    r'|greasy paws.{0,20}(burgum|secretary)'
    r'|\b(8647|fdt)\b'
    r'|\bno kings\b'
    r'|(impeach|arrest|lock (him|them) up).{0,20}trump'
    r'|trump.{0,30}(prison|jail|convicted|felon|criminal)'
    r'|(traitor|treason).{0,20}trump|trump.{0,20}(traitor|treason)'
    r'|(trump|president trump).{0,40}(called|said|stated|tweeted|posted|declared).{0,60}(trash|dump|garbage|disgusting|horrible|terrible|awful|wasteland|disgrace)'
    r'|(secretary|hegseth|hhs).{0,30}(killed|shot|dumped|hunted).{0,30}(bear|animal|wildlife)'
    r'|(denali|mckinley).{0,60}(never (climbed|visited|discovered)|rename|insulting|native)'
    r'|trump.{0,40}(bigly|covfefe|very stable genius|person woman man camera tv)'
    r'|(bergum|hegseth|rfk|kennedy).{0,30}(fool|idiot|moron|disgrace|disaster|incompetent|ruining|destroying)'
    r'|trump.{0,60}(monopoly|flipping the board|game of monopoly|reality show|clown show)'
    r'|(checks and balances|bipartisan|poll worker).{0,50}(function|work|intend|as design|as intended)'
    r'|(nothing more orange|more orange than|spray.?tan).{0,20}(face|self|him|trump)'
    r'|(combover|comb.over).{0,30}(national security|threat)'
    r'|^somebody let a felon in[.!?\s]*$'
    r'|felon.{0,20}(let in|in the|running|president|office)',
    re.IGNORECASE
)

# "Hands off our history" and similar — opposition framing, not personal attack
HANDS_OFF = re.compile(
    r'(hands off (our|the) (history|parks|lands|heritage)|'
    r'(trump|this) administration.{0,30}hands off|'
    r'hands off.{0,30}(trump|this) administration)',
    re.IGNORECASE
)

PRO_PARKS = re.compile(
    r'(fund|funding|underfund|budget|resource|money|support).{0,30}(park|nps|ranger|staff|service)s?'
    r'|(more|additional|increase|restore|adequate|better).{0,20}(fund|budget|staff|ranger|resource|support).{0,30}(park|nps)'
    r'|(needs?|deserve|should have|must have).{0,20}(more|additional|better|adequate).{0,20}(fund|budget|staff|ranger|resource)'
    r'|hope (someone|congress|the government|administration).{0,20}(increase|restore|provide|give).{0,30}(fund|budget|resource)'
    r'|(hire back|rehire|restore|reinstate).{0,20}(ranger|staff|employee)'
    r'|(hire|need|want).{0,10}more.{0,20}(ranger|interpreter|historian|archaeologist|maintenance|clerical)'
    r'|(staffing|staff).{0,20}(cut|reduc|laid off|fired|depleted|too (few|low|thin))'
    r'|(sell|sold|selling|sale|privatize).{0,30}(public land|federal land|national park|park land|our land)'
    r'|(not for sale|belong to (the |all )?(people|american|public)|public lands (in )?public hands)'
    r'|(protect|preserve|save|defend|keep).{0,40}(national park|public land|nps|these parks|our parks).{0,20}(for|from|forever|always|future)'
    r'|(save|protect|defend|keep).{0,5}(the|our|these)?.{0,5}parks?[.!?]*$'
    r'|national park(s)? (is|are|remain|represent|embod|should|must|deserve|need|belong|have always)'
    r'|(national treasure|greatest idea|best idea|greatest gift|america.s greatest|one of (the best|our best|america.s best))'
    r'|(belong|belongs) to (all|every|the) american'
    r'|(for (future|coming|next) generations|generations to come)'
    r'|thank (you|the|our) (nps|national park service|park service|(to )?all (the |our )?(ranger|staff|employee|worker|nps))'
    r'|(ranger|staff|worker)s? (deserve|need|should (be|have|receive|get)).{0,40}(more|better|support|fund|resource|appreciation|pay)'
    r'|(renewed|newfound|deepened|great|profound|new).{0,20}(appreciation|respect|admiration|gratitude).{0,20}(for (all |the )?(ranger|park|nps|staff))'
    r'|(ranger|staff|nps).{0,30}(do (such|an amazing|incredible|important|vital|great|wonderful)).{0,20}(job|work)'
    r'|(national park|nps|parks?).{0,50}(increase|boost|generate|contribut|add).{0,30}(property value|economic|revenue|jobs|tourism|billion|million)'
    r'|thank.{0,30}(ranger|staff|nps|park).{0,30}(\d+[,.]?\d*|x \d+|thousand|hundred|million)'
    r'|(every|all).{0,20}american(s)? (should|deserve|need|must).{0,20}(visit|experience|have access|be able to enjoy)'
    r'|(i have (been coming|visited|been here|come here).{0,20}(for \d+|every year|many|multiple|several|my whole))'
    r'|(cut|cutting|cuts|slash|reduc).{0,60}(fund|budget|staff|employee).{0,60}(park|nps)'
    r'|(fund|budget).{0,20}(cut|cutting|cuts|reduc|slash)'
    r'|(staff|employee|ranger).{0,30}(cut|cutting|cuts|fired|laid off|eliminat)'
    r'|(stop.{0,15}cut|end.{0,10}cut|halt.{0,10}cut).{0,40}(park|nps|fund|staff)'
    r'|(lay off|laid off|firing|fired).{0,30}(federal|park|nps).{0,20}(employee|worker|staff)'
    r'|(importance|value|significance).{0,20}(national park|nps).{0,30}(cannot|can.t).{0,20}overstat'
    r'|(essential|vital|irreplaceable|invaluable).{0,20}(national park|public land|nps)'
    r'|(our|the|these)? ?parks? (are|is|remain) (essential|vital|irreplaceable|invaluable)'
    r'|keep (your|their|his|her).{0,10}hands off'
    r'|hands off our (national parks?|public lands?)'
    r'|^(more rangers?)[.!?\s]*$'
    r'|thank you.{0,20}(park rangers?|nps staff|staff).{0,30}(all you do|everything|hard work|dedication)'
    r'|thank you to (the|our|all).{0,10}(park rangers?|nps workers?|park staff)'
    r'|give.{0,20}(park rangers?|nps|national park).{0,30}(back.{0,20})?(funding|fund|resource|money|staff)'
    r'|(nps|national park service).{0,50}(lost|cut|fired|laid off).{0,50}\d+%.{0,50}(staff|employee|ranger)'
    r'|semiquincenten'
    r'|(fucking rich|it is rich|it.s rich).{0,60}public'
    r'|treated.{0,30}(terribly|badly|poorly|unfairly).{0,30}(administration|government)',
    re.IGNORECASE
)

# Extended park-visit signals: specific visit experiences without political content
PARK_VISIT_EXT = re.compile(
    r'(our|my) (visit|trip|hike|stay|experience|time here|time at|vacation)'
    r'|(i|we|my family|our family).{0,20}(visited|went to|hiked|camped|drove through|toured|took a tour|came here|stopped by).{0,60}(today|yesterday|last (week|month|summer|year|spring|fall|winter)|this (morning|afternoon|weekend|week)|recently|just|\d+ (day|week|month|year)s? ago)'
    r'|(we|i|my family).{0,20}(just|recently|finally) (visited|went|hiked|arrived)'
    r'|(on (my|our) (visit|trip|hike|tour|stay))'
    r'|(first|second|third|\d+(st|nd|rd|th)) time (visiting|here|at this|coming)'
    r'|ranger [A-Z][a-z]+ (was|is|did|helped|showed|gave|led)'
    r'|(guided hike|ranger.led|ranger.guided|ranger program|ranger talk|ranger walk).{0,20}with (ranger |[A-Z])'
    r'|(hike|hik(ing|ed)).{0,30}(last (week|weekend|month|summer|year)|yesterday|today|this (morning|afternoon|weekend))'
    r'|(loved|enjoyed) (hiking|the hike|our hike|our walk).{0,30}(here|at|in|last|this)'
    r'|(we|i) (saw|spotted|watched|observed|photographed|encountered).{0,50}(bison|bear|elk|wolf|deer|eagle|moose|geyser|waterfall|glacier|wildflower|hoodoo|arch|canyon|cave|snake|whale|seal|dolphin|puffin|condor)'
    r'|(proposed|got (engaged|married)|popped the question).{0,30}(here|at|in this)'
    r'|(staff|employee|volunteer|ranger).{0,40}(was not|were not|ignored|talking to each other|not (helpful|available|welcoming|present|there))'
    r"|(no one|nobody|staff).{0,30}(came|helped|acknowledged|greeted|welcomed) (me|us)"
    r"|(don't|do not|wouldn't|no need to) change (a|any|one) thing"
    r'|(no (notes|complaints|negatives|issues|problems)|nothing (to change|negative|to report|wrong))[.!]*'
    r'|(outraged|appalled|disappointed).{0,40}(eagle|bison|animal|bird|fish|squirrel|chipmunk)'
    r'|shortage of (park )?(ranger|staff|personnel|employee)'
    r'|(technology|interactive|exhibit|display).{0,30}(outdated|old|broken|not working|behind|2012|2013|2014|2015)'
    r'|(trail|path|route).{0,30}(need.{0,10}(better|more|clearer)|not.{0,10}(mark|sign|label|clear|well))'
    r'|(no sign|no marker|poorly marked|hard to find|confusing).{0,30}(trail|path|route)'
    r'|ranger.{0,20}(program|talk|tour|walk|hike).{0,50}(january|february|march|april|may|june|july|august|september|october|november|december|\d{1,2}/\d{1,2}|\d{4})'
    r'|ranger.{0,20}(led|guided).{0,30}(program|tour|hike).{0,30}(fantastic|great|amazing|wonderful|excellent|informative|enjoyed)'
    r'|ranger [A-Z][a-z]+.{0,60}(trail|out on the|helped|fantastic|great|amazing|wonderful)'
    r'|(infest|infestation|bug|insect|pest).{0,30}(tower|trail|area|building|lookout)'
    r'|(tower|trail|area|building|lookout).{0,30}(infest|infestation)'
    r'|(bridge|board|plank|railing|step).{0,30}(missing|broken|damaged|rotting|unsafe|needs repair)'
    r'|(excellent|wonderful|great|fantastic).{0,15}(facility|center|interpretive|visitor)'
    r'|(ranger|volunteer|staff|attendant|employee).{0,30}(was|were|is|are).{0,10}(excellent|amazing|wonderful|fantastic|great|friendly|helpful|knowledgeable|professional)'
    r'|(excellent|friendly|helpful|positive|amazing|wonderful|fantastic).{0,40}(attitude|manner|service|helpfulness) of (the|a) (ranger|volunteer|staff|attendant)'
    r'|(parking attendant|entrance station|fee booth|visitor services|front desk).{0,40}(friendly|helpful|excellent|amazing|great|wonderful|professional)',
    re.IGNORECASE
)

SHORT_POSITIVE = re.compile(
    r'^(beautiful|amazing|gorgeous|stunning|breathtaking|incredible|wonderful|'
    r'magnificent|perfect|fantastic|great|awesome|loved it|loved this|great visit|'
    r'wonderful visit|amazing visit|love this park)[!.,:;\s]*$'
    r'|^(staff (were|was|are|is)|rangers? (were|was|are|is)).{0,30}'
    r'(amazing|wonderful|incredible|excellent|great|fantastic|awesome|superb|helpful|friendly|knowledgeable)[!.]*$'
    r'|^(take care of (all )?our national parks)[!. ]*$',
    re.IGNORECASE
)


FACILITY = re.compile(
    r'(elevator|bathroom|restroom|toilet|parking (lot|space|fee|pass)|'
    r'trail (is|was) (closed|damaged|overgrown|blocked|washed out|eroded)|'
    r'shower.{0,20}(mold|broken|dirty|hot water|cold water)|'
    r'faucet|broken (fence|gate|bench|railing|bridge|equipment|fixture)|'
    r'reservation system|vehicle reservation|timed entry permit|'
    r'campground (full|overbooked|flooded|damaged|noisy|dirty)|campsite|'
    r'visitor center (is|was) (closed|locked|unstaffed|not open)|'
    r'porta.?potty|pit toilet|composting toilet|'
    r'cell (service|reception|signal) (is|was) (poor|bad|nonexistent|terrible)|'
    r'entrance fee|day.use fee|too expensive|not worth the fee|cost too much|'
    r'picnic table (is|was|are|were) (broken|damaged|dirty|missing)|'
    r'speed limit|road (is|was) (closed|damaged|washed out|flooded|unpaved)|'
    r'ADA|wheelchair|accessibility|accessible|handicap)',
    re.IGNORECASE
)

# Pure personal attacks on named individuals
# "Hands off our history" and similar — opposition framing, not personal attack
HANDS_OFF = re.compile(
    r'(hands off (our|the) (history|parks|lands|heritage)|'
    r'(trump|this) administration.{0,30}hands off|'
    r'hands off.{0,30}(trump|this) administration)',
    re.IGNORECASE
)

OFF_TOPIC = re.compile(
    r'(bigfoot|sasquatch|cryptid|loch ness|alien.{0,20}(park|ufo)|'
    r'cornfield backwards|according to all known laws of aviation|bee movie|'
    r'snitch.{0,20}(gold ball|wings|broom|harry potter|quidditch)|'
    r'small gold ball.{0,20}wings|flying.{0,20}(gold|snitch).{0,20}(wings|ball)|'
    r'drain the ocean|put the land bridge back|'
    r'bald eagle.{0,20}(steak|reprimand|finest|dining)|'
    r'alligator auschwitz|'
    r'democratic party of florida.{0,20}ceo|psychopathic savior|semitic blood|'
    r'my dog (can.t|cannot) swim.{0,20}(lifeguard|no lifeguard))',
    re.IGNORECASE
)


def classify_original(text):
    if pd.isna(text): return 'other_substantive'
    t = str(text)
    length = len(t.strip())

    # ── Off-topic / jokes / spam ──────────────────────────────────────────────
    if OFF_TOPIC.search(t): return 'off_topic_weird'
    if length <= 6: return 'off_topic_weird'
    if length < 30 and re.search(r'\b(fuck|shit|ass|bitch|cock)\b', t, re.I): return 'off_topic_weird'
    # Very short entries with no park/history/political content (true nonsense/test submissions)
    if length < 22 and not POLITICAL.search(t) and not PERSONAL_ATTACK.search(t) and not re.search(
            r'(park|history|sign|nps|national|land|exhibit|trail|fund|ranger|rename|staff|name)', t, re.I):
        return 'off_topic_weird'

    # ── Pro-removal ───────────────────────────────────────────────────────────
    if PRO_REMOVAL.search(t) and not QR_SIGN.search(t):
        return 'pro_removal'

    # ── Flagged signage ───────────────────────────────────────────────────────
    if (INTERPRETIVE_SIGN_CRIT.search(t)
            and not QR_SIGN.search(t)
            and not QR_QUOTE.search(t)
            and not HISTORY_PRIMARY.search(t)):
        return 'reporting_signage'

    # ── Defend history check before park visit — prevents staff comments
    # from overriding substantive history arguments ──────────────────────────
    if HISTORY_PRIMARY.search(t) and not QR_SIGN.search(t):
        return 'defend_history'

    # ── Park visit experience ─────────────────────────────────────────────────
    if SHORT_POSITIVE.match(t.strip()) and not POLITICAL.search(t):
        return 'genuine_complaint'
    if PARK_VISIT_EXT.search(t) and not POLITICAL.search(t):
        return 'genuine_complaint'
    if FACILITY.search(t) and not POLITICAL.search(t):
        return 'genuine_complaint'

    # ── Trump/Burgum criticism ────────────────────────────────────────────────
    if PERSONAL_ATTACK.search(t) and not HANDS_OFF.search(t):
        if not HISTORY_PRIMARY.search(t):
            return 'anti_trump_admin'

    # ── Defend historical accuracy ────────────────────────────────────────────
    if HISTORY_PRIMARY.search(t):
        return 'defend_history'

    # ── General pro-parks support ─────────────────────────────────────────────
    if PRO_PARKS.search(t):
        return 'pro_parks_general'

    # ── General opposition to the order ──────────────────────────────────────
    if QR_SIGN.search(t):
        return 'other_substantive'

    # ── Other substantive ────────────────────────────────────────────────────
    other_patterns = [
        r'(sell|sold|sale).{0,30}(land|acre|public|federal|forest|blm)',
        r'(doge|24 percent|24%).{0,30}(cut|fire|laid|staff)',
        r'(staff|employee|ranger).{0,30}(cut|fire|laid off|doge|reduc)',
        r'(climate change|global warming).{0,30}(real|science|import)',
        r'native (american|people|tribe).{0,60}(more|history|import|includ|should)',
    ]
    if any(re.search(p, t, re.I) for p in other_patterns):
        return 'other_substantive'

    if re.search(
        r'(great|amazing|beautiful|love|wonderful|fantastic|excellent|gorgeous|stunning)'
        r'.{0,30}(park|place|site|monument|visit|experience|trail|view)',
        t, re.I
    ) and not POLITICAL.search(t):
        return 'pro_parks_general'

    return 'other_substantive'

def classify_row(row):
    text = row[FEEDBACK_COL]
    tmpl = detect_template(text)
    if tmpl is not None:
        return tmpl
    return classify_original(text)


print("Running v6 classifier...")
df['category'] = df.apply(classify_row, axis=1)

print("\n=== V6 RESULTS ===")
vc = df['category'].value_counts()
print(vc.to_string())

template_cats = [c for c in vc.index if c.startswith('template_')]
flagged_n = df['category'].isin(['reporting_signage', 'pro_removal']).sum()
print(f"\nFlagged / supported removal: {flagged_n} ({flagged_n/len(df)*100:.2f}%)")
print(f"Original (non-template): {len(df) - df['category'].isin(template_cats).sum()}")

df.to_csv('/home/claude/classified_v6.csv', index=False)
print("\nSaved to classified_v6.csv")
