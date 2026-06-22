# The AI Shutdown Nobody Can Fully Explain

At 5:21 p.m. Eastern time on June 12, 2026, a directive from the United States government reached Anthropic.

The order, as Anthropic described it, cited national-security authorities and required the company to suspend access to its two newest artificial-intelligence models, Claude Fable 5 and Claude Mythos 5, for every foreign national. It did not matter whether the person was in Beijing, London, Toronto, or working inside Anthropic's own American offices.

The practical result was even broader. Anthropic said it could not continue operating the models while ensuring compliance, so it removed them for everyone.

Three days after launch, two of the world's most capable AI systems went dark.

The government has not publicly released the directive. It has not published a detailed technical explanation of the danger it believed it was stopping. It has not identified a public standard showing why these models, but apparently not comparable systems, required an emergency restriction this broad.

Anthropic has supplied its own explanation. The company said the government appeared to be reacting to a method for bypassing, or jailbreaking, safeguards built around Fable 5. Anthropic said the demonstration involved using the model to inspect a codebase and identify a small number of previously known, minor software vulnerabilities. It further claimed that other publicly available models could find the same flaws without a bypass.

Those are Anthropic's claims. The public cannot independently test them against the directive or the government's complete evidence.

That evidentiary gap is the real story.

The shutdown did not merely interrupt a product launch. It exposed a frontier-AI governance system in which a company can release a model with potentially dangerous cyber capabilities, the government can restrict it through a private legal instrument, and the public may be left with two opposing risk assessments and no independent way to determine which one justified the outcome.

The central question is not whether powerful AI can create cybersecurity risks. Anthropic itself says it can. The question is whether the United States contained an exceptional threat on June 12, or whether an opaque intervention removed a powerful defensive tool without publicly demonstrating that the response matched the risk.

## Three Days Earlier

Anthropic launched Claude Fable 5 and Claude Mythos 5 on June 9.

The names described two versions of the same underlying model. Fable 5 was the generally available version. Mythos 5 was the restricted version made available to a vetted group of cybersecurity and infrastructure organizations.

According to [Anthropic's launch announcement](https://www.anthropic.com/news/claude-fable-5-mythos-5), the model exceeded the capabilities of any system the company had previously made generally available. Anthropic promoted gains in software engineering, long-running autonomous work, scientific research, vision, and complex knowledge work. It also emphasized that those gains carried new risks.

Cybersecurity is inherently dual-use. The ability to inspect a huge codebase and locate a hidden flaw can help a maintainer patch vulnerable software. The same ability can help an attacker find an entry point. A model capable of writing a fix may also be capable of developing an exploit. The line between defense and offense often depends less on the technical instruction than on who requested it, what system they are targeting, and what they do next.

Anthropic said Mythos-class models had crossed a significant threshold. Its [technical assessment of Mythos Preview](https://red.anthropic.com/2026/mythos-preview/) reported that the earlier model could identify and exploit previously unknown vulnerabilities in major operating systems and web browsers. The company said nonexpert employees had prompted the model to look for remote-code-execution vulnerabilities and returned to find working exploits. Many details could not be published because affected software had not yet been patched.

Those are extraordinary claims, but they come from the model's developer. Independent verification remains limited by the same responsible-disclosure rules that prevent researchers from publishing live vulnerabilities. Anthropic's public reports provide meaningful evidence of capability, but not a complete outside audit.

Fable 5 was Anthropic's attempt to make the underlying capability broadly available with additional controls.

The model used classifiers intended to recognize risky requests involving cybersecurity, biology, chemistry, or attempts to reproduce frontier-model capabilities. When a classifier activated, the system could route the request to the less capable Claude Opus 4.8. Anthropic said these controls triggered in fewer than 5 percent of sessions on average, although some harmless requests would also be caught.

Mythos 5 removed some of the cyber restrictions. Access was limited to approved Project Glasswing organizations, including cyber defenders and critical-software providers. Anthropic described Mythos 5 as having the strongest cybersecurity capability of any model in the world.

The company did not claim the safeguards were perfect. Its launch materials said no model developer had created defenses guaranteed to resist every sustained attempt at bypass. Anthropic acknowledged that external testing by the United Kingdom's AI Security Institute had made progress toward a broad jailbreak within a limited testing period. The company nevertheless said thousands of hours of internal, government, and third-party testing had failed to produce a universal bypass before launch.

That caveat matters. The public debate after June 12 has sometimes been framed as a safety-conscious company being punished despite having solved model safeguards. Anthropic's own record does not support that simplified story. The company explicitly recognized residual risk. It released Fable because it believed layers of classifiers, monitoring, data retention, red teaming, and rapid response reduced that risk to an acceptable level.

The government apparently reached a different conclusion.

## The Defensive Network That Lost Access

The shutdown's consequences cannot be understood without Project Glasswing.

Anthropic launched the initiative in April after testing Mythos Preview. Its premise was that highly capable cyber models would proliferate whether or not Anthropic released one publicly. Rather than wait for attackers to gain equivalent tools, the company wanted defenders to find and patch vulnerabilities first.

The initial group included roughly 50 partners. In a [May update](https://www.anthropic.com/research/glasswing-initial-update), Anthropic said the project had found more than 10,000 high- or critical-severity vulnerabilities across important software. It also said the bottleneck had shifted. Finding flaws was becoming faster than verifying, disclosing, and repairing them.

That claim describes both the promise and danger of frontier cyber models. A machine that discovers weaknesses at unprecedented speed can overwhelm the institutions responsible for fixing them. Even defensive discovery creates a stockpile of sensitive information. Each unpatched vulnerability becomes dangerous if reports leak, systems are compromised, or the same flaw is independently found by an attacker.

On June 2, Anthropic announced that it was [expanding Project Glasswing](https://www.anthropic.com/news/expanding-project-glasswing) to approximately 150 additional organizations in more than 15 countries. The new participants included organizations connected to power, water, healthcare, communications, hardware, open-source software, and other infrastructure. Anthropic estimated that, for most partners, a major attack on their software could affect more than 100 million people.

The expansion had been developed through collaboration with the security industry, open-source maintainers, Project Glasswing partners, and the U.S. government.

Ten days later, the government directive reportedly prohibited every foreign national from accessing the newest Glasswing model.

That did not necessarily mean the government rejected the entire project. A national-security agency could reasonably distinguish between earlier Mythos access and the new model's greater capability. It could also possess intelligence about attempted foreign acquisition, a particular vulnerability, or an adversary that Anthropic did not know about.

But the breadth created a direct collision with Glasswing's international design. Critical software is developed across borders. American companies employ foreign nationals. Cloud platforms are used by multinational teams. Allied governments and infrastructure operators depend on code maintained by people with different citizenships in multiple jurisdictions.

A location restriction can be enforced through network and account controls, even if imperfectly. A nationality restriction requires a provider to know not merely where a person is but their legal status. It raises difficult questions about employees, dual nationals, contractors, shared enterprise accounts, automated agents, and cloud systems running on behalf of global organizations.

Anthropic said the order forced it to disable both models for all users. The public record does not establish that universal shutdown was the only technically possible response or that the government explicitly ordered that result. It establishes that Anthropic chose global removal as the way to comply immediately.

That distinction is important. The government is responsible for the directive it issued. Anthropic is responsible for its compliance design and public characterization. Without the letter, the public cannot tell where one decision ended and the other began.

## What The Government Has Not Explained

The phrase "export control" normally evokes physical items: advanced chips, manufacturing equipment, weapons components, or technical data sent across borders. Modern export law can also apply to software, services, and access by foreign persons inside the United States, sometimes called a deemed export.

The June 12 action appears to push that logic into new territory: access to the behavior of a cloud-hosted frontier model.

Brian Egan, a former legal adviser to the National Security Council and State Department, wrote in a [June 15 analysis for Just Security](https://www.justsecurity.org/142745/law-anthropic-export-controls/) that the likely authority was the Export Control Reform Act of 2018. He explained that the Commerce Department can privately inform a company that a license is required for activity the department believes may involve weapons of mass destruction. Such "is-informed" letters have been used with exports of semiconductor technology and specific counterparties.

Egan described the apparent breadth of the Anthropic order as unprecedented. Unlike a restriction focused on a named foreign organization or country, Anthropic said the directive covered every foreign national anywhere, including people lawfully working in the United States.

The analysis is informed inference, not documentary confirmation. The directive is not public. Anthropic's statement said only that it cited national-security authorities. Media reports have identified Commerce Secretary Howard Lutnick and the Bureau of Industry and Security, but the government has not provided the complete record on which a legal conclusion could rest.

Several fundamental questions therefore remain unanswered.

What precise law or regulation did the government invoke? Was Anthropic given an opportunity to seek a license or propose narrower safeguards? Was the directive temporary while an investigation continued, or indefinite? Did it contain classified findings omitted from Anthropic's account? Did it apply because of cybersecurity capability, biology capability, model autonomy, a specific attempted acquisition, or a combination of concerns?

Most importantly, what made Fable 5 and Mythos 5 different from competing models?

Anthropic said the government appeared to rely on a report demonstrating a narrow jailbreak. The company said it reviewed what it believed was the relevant report and concluded that the demonstrated capability was widely available elsewhere. Anthropic also said it had received only verbal evidence from the government and no example of a bypass producing a distinctly harmful result.

The government may have reasons it cannot disclose. Publishing an exploit could endanger systems before patches are available. Describing an intelligence source could reveal surveillance methods. Identifying a suspected foreign actor could compromise an investigation.

Secrecy can be necessary in cybersecurity. But secrecy also makes it impossible to evaluate consistency. If the government restricts one provider based on a standard it does not publish, neither competing companies nor the public can know whether equivalent risks are receiving equivalent treatment.

That concern is heightened by the history between Anthropic and the administration.

Earlier in 2026, Anthropic and the Department of War fought publicly over restrictions on military uses involving mass domestic surveillance and fully autonomous weapons. The department designated Anthropic a supply-chain risk. Anthropic challenged the action in federal court. The litigation remains part of the context surrounding the June directive.

It is fair to ask whether that conflict influenced the government's approach. It is not fair, on the available evidence, to state that the export action was retaliation. Timing, hostility, and differential treatment can support an investigative question. They do not prove motive.

## Two Competing Risk Stories

The strongest case for government intervention begins with Anthropic's own warnings.

The company said Mythos-class systems could lower the skill, time, and cost required to find and exploit serious software vulnerabilities. It reported that the model could chain multiple weaknesses, escape security boundaries, reverse-engineer exploits, and act with increasing autonomy. It acknowledged that no safeguard was perfectly resistant to jailbreaking.

If a foreign intelligence service obtained unrestricted or successfully bypassed access, the model could potentially help identify weaknesses in infrastructure, government systems, communications products, or widely used software. A model does not need to provide a magical one-click cyberweapon to create danger. A modest increase in speed multiplied across many targets can matter strategically.

The government may also have been acting under uncertainty. National-security decisions are often made before damage occurs. Waiting for a model-assisted intrusion to prove the risk would defeat the purpose of prevention.

The nationality-based scope may reflect concerns about deemed exports, insider access, or state-directed researchers operating through legitimate institutions. Restricting only users connecting from hostile countries would not address foreign agents, proxy organizations, or controlled personnel located elsewhere.

There is another factor: Anthropic is not a neutral evaluator of its own release. The company invested heavily in the models, marketed their capabilities, sold access, and was reportedly preparing for major financial activity. A global shutdown imposed immediate business and reputational costs. Its technical rebuttal deserves scrutiny rather than automatic acceptance.

The strongest case against the intervention is not that no risk existed. It is that the public facts do not explain why this particular response was coherent.

Anthropic said the cited demonstration involved a narrow bypass producing minor, already-known findings. If that description is accurate, equivalent capabilities were already available through other public models. Removing Fable would therefore inconvenience legitimate users without denying adversaries meaningful capability.

The restriction also removed Mythos 5 from vetted defenders participating in a program built with U.S. government collaboration. An [open letter signed by cybersecurity executives and technical leaders](https://freefable.org/) argued that taking advanced tools away from defenders while adversaries were progressing could increase risk. The signatories asked for the models to be restored and for future decisions to use an open, scientific, and transparent assessment process.

That letter represents expert advocacy, not proof. Some signatories may have commercial, professional, or ideological interests in broad model access. They also do not possess the complete classified record.

Still, the defensive-access argument has substance. Attackers need to find one exploitable weakness. Defenders must locate, verify, prioritize, patch, test, and deploy fixes across huge software ecosystems. If AI accelerates discovery for both sides, defenders may need the strongest available systems simply to keep pace.

The problem is not solved by declaring access either safe or unsafe. The risk changes depending on who uses the model, which safeguards are active, what monitoring exists, how findings are handled, and how quickly vulnerable systems can be patched.

Fable 5 and Mythos 5 embodied two different answers. Fable attempted broad access with automated controls. Mythos used organizational vetting and narrower distribution. The directive reportedly treated both as unavailable to all foreign nationals.

That is one reason the missing directive matters. A technically grounded order should explain why the safeguard distinction was insufficient.

## The Policy Contradiction

The timing becomes more striking when compared with two White House actions earlier that month.

On June 2, President Donald Trump signed an [executive order on advanced AI innovation and security](https://www.whitehouse.gov/presidential-actions/2026/06/promoting-advanced-artificial-intelligence-innovation-and-security/). It directed federal agencies to expand access to covered frontier models for cybersecurity defense, create benchmarks for evaluating advanced cyber capabilities in classified environments, build a voluntary framework for pre-release collaboration with developers, and establish a clearinghouse for AI-discovered vulnerabilities.

The order recognized the central Glasswing problem: finding vulnerabilities faster is not enough if institutions cannot verify and repair them. A clearinghouse could coordinate disclosure and patching while benchmarks could help the government compare models using a consistent standard.

Three days later, [National Security Presidential Memorandum 11](https://www.whitehouse.gov/presidential-actions/2026/06/national-security-presidential-memorandum-nspm-11/) ordered faster AI adoption across intelligence and warfighting. It called for deep partnerships with industry and broad availability of advanced frontier models to national-security professionals. It also required systems to be reliable, controllable, secure, and available when missions depend on them.

The memorandum included an assurance principle: commercial entities or adversaries should not be able to disable or materially modify mission systems without federal knowledge and approval.

That language reflects a concern exposed by the Anthropic dispute. Governments increasingly depend on privately developed models whose providers maintain technical and policy control. Anthropic had already resisted certain military uses. The government wanted assurance that a vendor could not withdraw capability during a conflict.

Yet on June 12, the government itself reportedly triggered the withdrawal of Anthropic's most capable models from all users, including vetted defenders.

These positions are not necessarily irreconcilable. The administration can favor rapid adoption of systems it considers secure while restricting a model it believes crossed an unacceptable threshold. It can support voluntary collaboration generally and use compulsory authority in an emergency.

But the policies create an obligation for consistency. If frontier models are essential to national security, restricting access should be based on a credible, repeatable standard. If voluntary pre-release testing is preferred, developers need to know what findings can trigger compulsory withdrawal. If model diversity prevents dangerous dependence on one vendor, singling out one provider without explaining the comparative standard can undermine that goal.

The June 2 order may eventually create institutions capable of resolving disputes like this one. On June 12, those mechanisms were either not ready or not used publicly.

The result was governance by private letter.

## The Standard No One Can See

Several conclusions are supported by the record.

Fable 5 and Mythos 5 were unusually capable systems with real dual-use cybersecurity risk. Anthropic knew that and said so before launch. It attempted to manage the risk through automated safeguards, monitoring, data retention, testing, and restricted trusted access.

The U.S. government concluded that additional intervention was necessary. According to Anthropic, the directive applied to all foreign nationals. Anthropic then disabled both models globally.

The government may possess evidence that justifies that action. Anthropic may be understating the risk of its own product. Cybersecurity professionals asking for restoration may underestimate intelligence threats or overvalue defensive access.

None of those possibilities changes the public-accountability problem.

A decision with global consequences was made under a standard the public cannot inspect. The company affected by it became the main source for what the directive said. Independent experts could evaluate general capability and legal theory, but not the complete evidence. Users, allies, and competing developers were left to infer the rules from the outcome.

Frontier AI will make this problem recur. Governments will encounter models whose capabilities are difficult to measure, easy to distribute through cloud services, and useful for both defense and attack. Developers will have commercial incentives to release them and reputational incentives to defend their safeguards. Intelligence agencies will sometimes hold information that cannot be made public.

The solution cannot be total transparency. Publishing a live jailbreak or unpatched vulnerability could cause the harm regulation is meant to prevent.

But total opacity is not a durable system either.

A credible process would separate sensitive technical evidence from public reasoning. It could use cleared independent evaluators, defined capability thresholds, confidential adversarial testing, comparable review across providers, time-limited emergency restrictions, and public explanations of legal authority and decision criteria. It could provide an appeals path without requiring the disclosure of exploitable details.

The White House's own June orders point toward parts of that structure: classified benchmarks, a vulnerability-clearinghouse, pre-release collaboration, diverse suppliers, and assurance requirements. The Anthropic shutdown shows why those pieces need to become an accountable process rather than a collection of aspirations.

For now, the public record supports neither a simple story of reckless government censorship nor one of an obviously necessary security recall.

It supports a more troubling conclusion.

One of the most consequential AI safety decisions yet made was carried out before the public had any way to judge the standard behind it. The models disappeared. The risk assessment did not.

Until the government releases a redacted directive, identifies its authority, or explains the technical threshold it applied, the shutdown will remain what it was at 5:21 p.m. on June 12: a national-security decision whose impact was immediate and whose justification is still largely hidden.

## Reporting Method And Limits

This investigation relies primarily on public statements, technical reports, executive actions, and court records available as of June 22, 2026. Claims made by Anthropic about the directive, the jailbreak demonstration, model safeguards, vulnerability severity, and Project Glasswing results are attributed to Anthropic because the underlying government letter, test artifacts, and most affected vulnerability reports are not public. White House documents establish administration policy but do not independently disclose the basis for the June 12 directive. Legal analysis is used to explain a plausible statutory mechanism, not to make a definitive legal finding.

No attempt was made to reproduce a jailbreak, obtain unpublished exploit details, or identify unpatched vulnerabilities. Such testing could create operational risk and would not resolve the central documentary gap. The investigation also does not treat a missing public explanation as evidence that no classified justification exists.

Requests for additional records and responses from the government, Anthropic, independent evaluators, and affected Project Glasswing organizations would be necessary before representing the account as original reporting rather than a public-record investigation. Any later response that materially changes the evidence should be incorporated before publication.

## Source Ledger

Primary documentation:

- [Anthropic directive statement](https://www.anthropic.com/news/fable-mythos-access)
- [Fable 5 and Mythos 5 launch documentation](https://www.anthropic.com/news/claude-fable-5-mythos-5)
- [Fable 5 and Mythos 5 system card](https://www-cdn.anthropic.com/d00db56fa754a1b115b6dd7cb2e3c342ee809620.pdf)
- [Project Glasswing expansion](https://www.anthropic.com/news/expanding-project-glasswing)
- [Project Glasswing initial update](https://www.anthropic.com/research/glasswing-initial-update)
- [Mythos Preview cybersecurity assessment](https://red.anthropic.com/2026/mythos-preview/)
- [White House AI innovation and security order](https://www.whitehouse.gov/presidential-actions/2026/06/promoting-advanced-artificial-intelligence-innovation-and-security/)
- [White House NSPM-11](https://www.whitehouse.gov/presidential-actions/2026/06/national-security-presidential-memorandum-nspm-11/)
- [Open letter on transparent AI cyber protections](https://freefable.org/)
- [Anthropic-Department of War federal docket](https://www.courtlistener.com/docket/72379655/anthropic-pbc-v-us-department-of-war/)

Analysis and corroboration:

- [Just Security legal analysis](https://www.justsecurity.org/142745/law-anthropic-export-controls/)
- [Axios cybersecurity-industry response](https://www.axios.com/2026/06/16/anthropic-fable-trump-white-house-cybersecurity)
- [TechCrunch cybersecurity open-letter report](https://techcrunch.com/2026/06/15/cybersecurity-vets-protest-dangerous-us-government-ban-on-anthropics-most-powerful-models/)
- [The Verge account of the dispute](https://www.theverge.com/ai-artificial-intelligence/950412/anthropic-trump-adminstration-claude-mythos-fable-5-export-controls)
