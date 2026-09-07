<p align="center">
<picture>
  <source media="(max-width: 700px)" srcset="./assets/profile-banner-m.jpg">
  <img src="./assets/profile-banner.jpg" width="100%" alt="Humanoid robot turning a gear beside a wireframe globe">
</picture>
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/nameplate-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/nameplate-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/nameplate.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/nameplate-light.svg">
  <img src="./assets/nameplate.svg" width="100%" alt="AMADEUS — Pedro Barbosa — Quantitative Developer and Systems Engineer — Rio de Janeiro, UTC−3, EN & PT, remote">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/at-a-glance.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/at-a-glance-light.svg">
  <img src="./assets/at-a-glance.svg" width="100%" alt="Quant research and backtesting · Backend in Go, PHP and Python · UTC−3 · English and Português">
</picture>
</p>

<p align="center">
  <a href="https://dilectusadeo.com/"><img src="https://img.shields.io/badge/Portfolio-1c2430?style=for-the-badge&logo=googlechrome&logoColor=e8eef6" alt="Portfolio"></a>
  <a href="mailto:barbosamaverickv8@gmail.com"><img src="https://img.shields.io/badge/Start_a_Project-c1121f?style=for-the-badge&logo=minutemailer&logoColor=e8eef6" alt="Start a project"></a>
  <a href="https://www.linkedin.com/in/pedro-barbosa-0143a6289/"><img src="https://img.shields.io/badge/LinkedIn-1c2430?style=for-the-badge&logo=linkedin&logoColor=e8eef6" alt="LinkedIn"></a>
  <a href="https://github.com/QuantConnect"><img src="https://img.shields.io/badge/QuantConnect-1c2430?style=for-the-badge&logo=quantconnect&logoColor=e8eef6" alt="QuantConnect"></a>
</p>

<p align="center">
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/h-work-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/h-work-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/h-work.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/h-work-light.svg">
  <img src="./assets/h-work.svg" width="100%" alt="What I work on">
</picture>
</p>

<p align="center">
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/w-quant-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/w-quant-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/w-quant.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/w-quant-light.svg">
  <img src="./assets/w-quant.svg" width="380" alt="Quantitative development — trading strategy research and backtesting on QuantConnect, risk modelling and predictive models on financial time series.">
</picture>
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/w-go-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/w-go-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/w-go.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/w-go-light.svg">
  <img src="./assets/w-go.svg" width="380" alt="Backend systems in Go — services that ship as a single static binary with no runtime dependencies, SQLite with full-text search, systemd deployment.">
</picture>
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/w-php-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/w-php-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/w-php.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/w-php-light.svg">
  <img src="./assets/w-php.svg" width="380" alt="PHP and legacy modernisation — registration and permission flows, scheduling, payments, reversible database migrations.">
</picture>
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/w-data-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/w-data-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/w-data.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/w-data-light.svg">
  <img src="./assets/w-data.svg" width="380" alt="Data automation — collection bots, scraping, pipelines and internal tooling on Linux and systemd.">
</picture>
</p>

> Most of what I build is private — client work, an employer's platform, and my own tooling. The public repositories below are the part I can show.

<p align="center">
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/h-selected-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/h-selected-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/h-selected.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/h-selected-light.svg">
  <img src="./assets/h-selected.svg" width="100%" alt="Selected work">
</picture>
</p>

**iode** — personal orchestration engine, in Go. Indexes projects, collects daily
activity and surfaces connections between them. Single static binary, SQLite with
FTS5, no CGO. Collectors run as subprocesses over a versioned JSON contract, so a
new data source never touches the core.

**Go suite** — `sentinel` for host integrity, `bounty` for ranking funded GitHub
issues, `rgbd`. One thesis across three programs: no CGO, one binary each,
deployed with systemd.

**[SOS](https://github.com/Amadeus-22/SOS)** — administrative system built end to
end, in JavaScript.

**Quantitative research** — strategy simulation and backtesting on
[QuantConnect](https://github.com/QuantConnect), with predictive modelling in
Python and R.

<p align="center">
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/h-currently-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/h-currently-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/h-currently.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/h-currently-light.svg">
  <img src="./assets/h-currently.svg" width="100%" alt="Currently">
</picture>
</p>

**Software Engineer at [TIIX](https://github.com/AM-TIIX)** — a health and services
platform ([tiix.com.br](https://tiix.com.br/)). I work on the PHP portals for
clients, professionals and brokers: registration and permission flows, scheduling,
payments, and the shared foundation beneath them. Legacy PHP in a WordPress-based
ecosystem, with reversible MySQL migrations.

<p align="center">
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/h-stack-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/h-stack-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/h-stack.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/h-stack-light.svg">
  <img src="./assets/h-stack.svg" width="100%" alt="Stack">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/stack.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/stack-light.svg">
  <img src="./assets/stack.svg" width="100%" alt="Go, Python, PHP, JavaScript, TypeScript, R, Bash · SQLite, PostgreSQL, MongoDB, scikit-learn · Linux, Docker, Git, GitHub, Node.js, React, Flask">
</picture>
</p>

<p align="center">
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/h-communities-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/h-communities-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/h-communities.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/h-communities-light.svg">
  <img src="./assets/h-communities.svg" width="100%" alt="Communities and organizations">
</picture>
</p>

<table>
<tr>
<td width="50%" valign="top">
  <a href="https://github.com/QuantConnect"><img src="https://github.com/QuantConnect.png?size=80" width="56" align="left" hspace="14" alt="QuantConnect"></a>
  <h3><a href="https://github.com/QuantConnect">QuantConnect</a></h3>
  <p>Algorithmic trading research and backtesting, on the platform behind <a href="https://github.com/QuantConnect/Lean">Lean</a>.</p>
</td>
<td width="50%" valign="top">
  <a href="https://github.com/AM-TIIX"><img src="https://github.com/AM-TIIX.png?size=80" width="56" align="left" hspace="14" alt="TIIX"></a>
  <h3><a href="https://github.com/AM-TIIX">TIIX</a></h3>
  <p>Health and services platform (<a href="https://tiix.com.br/">tiix.com.br</a>). Current employer.</p>
</td>
</tr>
<tr>
<td width="50%" valign="top">
  <a href="https://github.com/NER-ELOHIM"><img src="https://github.com/NER-ELOHIM.png?size=80" width="56" align="left" hspace="14" alt="NER-ELOHIM"></a>
  <h3><a href="https://github.com/NER-ELOHIM">NER-ELOHIM</a></h3>
  <p>My own organization, where the Go suite and the engineering tooling live. Private by design.</p>
</td>
<td width="50%" valign="top">
  <a href="https://github.com/instituto-nova-sos"><img src="https://github.com/instituto-nova-sos.png?size=80" width="56" align="left" hspace="14" alt="Instituto Nova SOS"></a>
  <h3><a href="https://github.com/instituto-nova-sos">Instituto Nova SOS</a></h3>
  <p>Contributor to <code>chesed</code>, a Go and TypeScript project for a social institute.</p>
</td>
</tr>
</table>

<p align="center">
<picture>
  <source media="(max-width: 700px) and (prefers-color-scheme: dark)" srcset="./assets/h-contact-m.svg">
  <source media="(max-width: 700px) and (prefers-color-scheme: light)" srcset="./assets/h-contact-m-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="./assets/h-contact.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/h-contact-light.svg">
  <img src="./assets/h-contact.svg" width="100%" alt="Contact">
</picture>
</p>

<p align="center">
  Open to <b>remote roles and contract work</b>: backend engineering,
  quantitative development and data automation.
</p>

<p align="center">
  <a href="mailto:barbosamaverickv8@gmail.com"><img src="https://img.shields.io/badge/barbosamaverickv8@gmail.com-c1121f?style=for-the-badge&logo=gmail&logoColor=e8eef6" alt="Email"></a>
  <a href="https://dilectusadeo.com/"><img src="https://img.shields.io/badge/dilectusadeo.com-1c2430?style=for-the-badge&logo=googlechrome&logoColor=e8eef6" alt="Website"></a>
</p>

