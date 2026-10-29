"""Shared vocabulary for the SYNTHETIC CRM feedback dataset.

Each theme is a customer problem or request. The generator writes feedback text
that contains one of the theme's key phrases; clean_data.py tags text with the
same key phrases (a rule-based tagger). The shared vocabulary means tagger
accuracy on this synthetic data is not evidence of real-world NLP accuracy.
"""
import re

CATS = ["Bug", "Feature Request", "Usability Issue", "Performance Issue", "Integration Issue"]
AREAS = ["Lead Management", "Contact Management", "Workflow Automation",
         "Reporting", "Integrations", "User Interface"]

# id: (label, area, category, base_weight, (starter, professional, enterprise) multipliers, keys, cores)
T = {}


def add(tid, label, area, cat, w, mult, keys, cores):
    T[tid] = dict(label=label, area=area, category=cat, weight=w, mult=mult, keys=keys, cores=cores)


add("lead_dup", "Duplicate leads created", "Lead Management", "Bug", 6, (1.1, 1, .8),
    ["duplicate lead records", "duplicated leads", "lead de-duplication failures"],
    ["Web form submissions keep creating {k}, and reps end up calling the same prospect twice.",
     "After every list import we find {k} that have to be cleaned up by hand.",
     "We are seeing {k} when a lead arrives from both the website and a trade-show list.",
     "There are {k} across our pipeline views and nobody knows which record is the source of truth."])
add("lead_score", "Automated lead scoring", "Lead Management", "Feature Request", 5, (1.1, 1, .8),
    ["automated lead scoring", "lead scoring rules", "a lead score model"],
    ["We need {k} so reps can focus on the prospects most likely to close.",
     "Please add {k} based on engagement, company size and recent activity.",
     "Would love to see {k} that marketing and sales can both tune.",
     "Right now reps rank leads by gut feel; {k} would fix that."])
add("lead_assign", "Lead routing is inflexible", "Lead Management", "Usability Issue", 3, (1.1, 1, .8),
    ["lead routing rules", "lead assignment settings", "round-robin lead assignment"],
    ["Setting up {k} takes too many steps and the options don't cover territories.",
     "The {k} are confusing and new leads sometimes sit unassigned over weekends.",
     "It is hard to understand how {k} decide who owns a lead.",
     "We can't combine region and deal size in the {k}."])
add("lead_slow", "Slow lead lists and pipeline board", "Lead Management", "Performance Issue", 3.5, (1.1, 1, .8),
    ["lead list loading", "pipeline board loading", "lead view load times"],
    ["The {k} gets very slow once we pass a few thousand open leads.",
     "Our {k} regularly exceeds ten seconds on Monday mornings.",
     "Complaint about {k}: the board freezes while cards render.",
     "Reps have stopped using the board because of {k}."])
add("contact_dedupe", "Bulk contact merge", "Contact Management", "Feature Request", 5, (.8, 1.2, 1.1),
    ["a bulk contact merge", "a tool to merge duplicate contacts", "contact de-duplication tooling"],
    ["We need {k} because our database has years of overlapping records.",
     "Please build {k} with a preview of what will be combined.",
     "Is there any plan for {k}? Merging one record at a time is not realistic.",
     "{k} that keeps activity history would save our ops team hours."])
add("contact_import", "Unreliable contact imports", "Contact Management", "Bug", 6, (1.5, 1, .6),
    ["contact CSV import", "import field mapping", "spreadsheet import"],
    ["The {k} fails halfway through with a generic error and no row-level detail.",
     "Our {k} scrambles phone and email columns even after we map them correctly.",
     "The {k} silently skipped rows and we only noticed days later.",
     "The {k} rejects files with accented characters in names."])
add("contact_search", "Slow contact search", "Contact Management", "Performance Issue", 3.5, (1, 1, 1),
    ["contact search", "saved contact filters", "contact list filtering"],
    ["Our {k} is slow and often returns stale results right after an update.",
     "The {k} times out on our largest accounts.",
     "Combining several conditions in {k} makes the page hang.",
     "We avoid {k} during calls because it takes too long."])
add("contact_custom", "Custom fields and hierarchy", "Contact Management", "Feature Request", 3, (.7, 1.1, 1.3),
    ["custom contact fields", "a contact relationship hierarchy", "an account hierarchy view"],
    ["We need {k} to reflect parent companies and subsidiaries.",
     "Please extend {k}; the current limit is too small for our use case.",
     "Requesting {k} so account managers can see who reports to whom.",
     "Lacking {k} forces us to keep a parallel spreadsheet."])
add("wf_builder", "Confusing workflow builder", "Workflow Automation", "Usability Issue", 6, (.9, 1.1, 1.0),
    ["workflow builder", "automation canvas", "workflow editor"],
    ["The {k} is hard to follow once a flow has more than a handful of steps.",
     "I can't tell what a branch does in the {k} without opening every node.",
     "Our new admins struggle with the {k}; there is no guidance or validation.",
     "The {k} doesn't let us copy steps between flows."])
add("wf_fail", "Workflows failing silently", "Workflow Automation", "Bug", 6, (.5, 1.2, 1.5),
    ["workflow failures", "automation misfires", "workflow runs failing silently"],
    ["We are hitting {k}: emails don't send and nobody gets notified.",
     "Since the last release we've had {k} and tasks are being created twice.",
     "Several {k} left deals stuck in the wrong stage.",
     "We found {k} only because a customer complained."])
add("wf_templates", "Workflow templates", "Workflow Automation", "Feature Request", 4.5, (.7, 1.2, 1.2),
    ["workflow templates", "prebuilt automations", "automation recipes"],
    ["Please provide {k} for common processes like onboarding and renewals.",
     "We'd adopt automation faster with {k} we could customize.",
     "A library of {k} would cut our setup time.",
     "Competitors ship {k}; we are rebuilding the same flows from scratch."])
add("wf_approval", "Approval steps in workflows", "Workflow Automation", "Feature Request", 2.5, (.3, 1, 2.0),
    ["approval steps", "a discount approval flow", "multi-level approvals"],
    ["We need {k} in workflows so managers can sign off on discounts.",
     "Adding {k} is a blocker for our finance team.",
     "Requesting {k}; today approvals happen over chat."])
add("rep_custom", "Custom and scheduled reports", "Reporting", "Feature Request", 6, (.6, 1.2, 1.4),
    ["a custom report builder", "scheduled report emails", "report scheduling"],
    ["We need {k} so non-technical managers can create their own views.",
     "Please add {k}; today an analyst rebuilds the same report every week.",
     "Requesting {k} so leadership gets numbers without logging in.",
     "Without {k} we export raw data and rebuild everything elsewhere."])
add("rep_export", "Broken report exports", "Reporting", "Bug", 4, (.8, 1.1, 1.1),
    ["Excel export", "report export", "CSV export of reports"],
    ["The {k} cuts off rows after a few thousand records.",
     "Our {k} drops formatting and shows dates as numbers.",
     "Finance can't rely on the {k}; totals don't match the screen.",
     "The {k} times out for date ranges longer than a quarter."])
add("rep_slow", "Slow dashboards", "Reporting", "Performance Issue", 4.5, (.6, 1, 1.6),
    ["dashboard loading", "report load time", "dashboard refresh"],
    ["The {k} is painfully slow with a full year of data.",
     "Our {k} spins for a minute before showing any chart.",
     "{k} got noticeably worse over the last few months.",
     "Execs gave up on the {k} and ask for screenshots instead."])
add("rep_forecast", "Sales forecasting", "Reporting", "Feature Request", 3, (.4, 1.1, 1.5),
    ["sales forecasting", "forecast rollups", "quota tracking"],
    ["We need {k} by team and region for quarterly planning.",
     "Please add {k}; managers keep a separate spreadsheet.",
     "Requesting {k} that updates as deal stages change."])
add("int_email", "Email and calendar sync drops", "Integrations", "Integration Issue", 6.5, (.8, 1.1, 1.0),
    ["Gmail sync", "Outlook calendar sync", "email sync"],
    ["Our {k} keeps disconnecting and activities are missing from the contact timeline.",
     "The {k} duplicates meetings and misses replies.",
     "After the token expires, {k} stops with no warning.",
     "Reps no longer trust {k}, so they log activity by hand."])
add("int_api", "API limits and webhook failures", "Integrations", "Integration Issue", 5, (.3, 1, 2.2),
    ["API rate limits", "webhook delivery", "API timeouts"],
    ["We keep hitting {k} during nightly syncs with our data warehouse.",
     "{k} is unreliable and there is no retry or log we can inspect.",
     "Hard to debug: {k} fail with vague error codes.",
     "Our integration partner flagged {k} as a risk for the project."])
add("int_native", "Native integrations", "Integrations", "Feature Request", 5, (.8, 1.2, 1.0),
    ["a native accounting integration", "a marketing automation connector", "a native Slack integration"],
    ["We would pay for {k} instead of maintaining Zapier chains.",
     "Please build {k}; our team copies data across systems daily.",
     "Requesting {k} to remove manual re-entry.",
     "Lack of {k} is a gap versus other CRMs we evaluated."])
add("int_sso", "SSO and provisioning", "Integrations", "Feature Request", 2.5, (.05, .5, 4),
    ["SSO support", "SCIM provisioning", "SAML login"],
    ["Our security team requires {k} before we can expand seats.",
     "Please add {k}; managing users by hand does not scale.",
     "Requesting {k} for our compliance audit."])
add("ui_mobile", "Mobile app", "User Interface", "Feature Request", 5.5, (1.3, 1, .8),
    ["a mobile app", "offline mobile access", "mobile call logging"],
    ["Our field reps need {k} to update deals between visits.",
     "Please prioritize {k}; the mobile web view is hard to use.",
     "We lose notes whenever reps are away from a desk without {k}.",
     "Requesting {k} so reps can log activity right after a meeting."])
add("ui_nav", "Cluttered navigation", "User Interface", "Usability Issue", 4, (1.6, 1, .5),
    ["navigation menu", "settings navigation", "page layout"],
    ["The {k} is cluttered and I can never find the setting I need.",
     "New hires get lost in the {k}; it takes weeks to learn.",
     "Too many clicks to reach common screens because of the {k}.",
     "The {k} changed and nobody told us where things moved."])
add("ui_perf", "Laggy pages", "User Interface", "Performance Issue", 4, (1.2, 1, .9),
    ["page lag", "UI freezing", "slow page transitions"],
    ["We notice {k} whenever more than a few tabs are open.",
     "The {k} gets worse in the afternoon.",
     "{k} makes data entry frustrating during live calls.",
     "Since the redesign there is more {k} on older laptops."])
add("ui_bulk", "Bulk actions", "User Interface", "Feature Request", 4, (.7, 1.2, 1.2),
    ["bulk edit actions", "bulk actions on lists", "multi-select actions"],
    ["We need {k} to update owners and stages for many records at once.",
     "Please add {k}; changing records one at a time wastes hours.",
     "Requesting {k} across every list view.",
     "Admins ask for {k} every time we reorganize territories."])

THEME_ORDER = list(T)


def _norm(s):
    return re.sub(r"^(an?|the)\s+", "", s.lower())


KEY_PATTERNS = {tid: [re.compile(re.escape(_norm(k)), re.I) for k in v["keys"]] for tid, v in T.items()}


def tag_text(text):
    """Return list of theme ids whose key phrase appears in text."""
    return [tid for tid, pats in KEY_PATTERNS.items() if any(p.search(text) for p in pats)]
