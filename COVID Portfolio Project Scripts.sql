select * from CovidDeaths
where continent is not null
order by 3,4

-- Data that we are going to use

select location, date, total_cases, new_cases, total_deaths, population
from CovidDeaths
where continent is not null
order by 1,2

-- Looking at total cases vs total deaths
-- Shows likelihood of dying if you contact covid in india

select location,date, total_cases, total_deaths, (total_deaths/nullif(total_cases,0))*100 as DeathPercentage
from CovidDeaths
where location like '%ndia%'
and continent is not null
order by 1,2

-- Looking at total cases vs population
-- Shows what percentage of population got covid

select location,date, population, total_cases, (total_cases/population)*100 as PercentPopulationInfected
from CovidDeaths
--where location like '%states%'
where continent is not null
order by 1,2
 

 -- Looking at countries with highest infection rate compared to population

select location, population, max(total_cases) as HighestInfection, Max((total_cases/population))*100 as PercentPopulationInfected
from CovidDeaths
--where location like '%states%'
where continent is not null
group by location, population
order by PercentPopulationInfected desc

-- Showing countries with highest death count per population

select location, MAX(total_deaths) as TotalDeathCount
from CovidDeaths
--where location like '%states%'
where continent is not null
group by location
order by TotalDeathCount desc

--Breakdown by continent
--Showing continents with highest death count per population

select continent, MAX(total_deaths) as TotalDeathCount
from CovidDeaths
--where location like '%states%'
where continent is not null
group by continent
order by TotalDeathCount desc

--Global Numbers

select SUM(new_cases) as total_cases, sum(new_deaths) as total_deaths, (sum(new_deaths)/SUM(nullif(new_cases,0)))*100 as DeathPercentage
from CovidDeaths
--where location like '%ndia%'
where continent is not null
--group by date
order by 1,2


-- Looking for total population vs vaccinations

select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations,
SUM(cast(vac.new_vaccinations as float)) over (partition by dea.location order by dea.location, dea.date ) as RollingPeopleVaccinated
from CovidDeaths dea
join CovidVaccinations vac
on dea.location = vac.location
and dea.date = vac.date
where dea.continent is not null
order by 2,3

-- Use CTE

with popvsvac (continent, location, date, population, new_vaccinations, RollingPeopleVaccinated)
as
(
select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations,
SUM(convert(float,vac.new_vaccinations )) over (partition by dea.location order by dea.location, dea.date ) as RollingPeopleVaccinated
from CovidDeaths dea
join CovidVaccinations vac
on dea.location = vac.location
and dea.date = vac.date
where dea.continent is not null
)
select * ,(RollingPeopleVaccinated/population)*100
from popvsvac


--Temp Table

drop table if exists #PercentPopulationVaccinated
create table #PercentPopulationVaccinated 
(
continent nvarchar(255),
location nvarchar(255),
date datetime,
population numeric,
new_vaccinations numeric,
RollingPeopleVaccinated numeric
)

insert into #PercentPopulationVaccinated
select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations,
SUM(convert(float,vac.new_vaccinations )) over (partition by dea.location order by dea.location, dea.date ) as RollingPeopleVaccinated
from CovidDeaths dea
join CovidVaccinations vac
on dea.location = vac.location
and dea.date = vac.date
--where dea.continent is not null


select * ,(RollingPeopleVaccinated/population)*100
from #PercentPopulationVaccinated


--Creating view to store data for later visualizations

create view PercentPopulationVaccinated as
select dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations,
SUM(convert(float,vac.new_vaccinations )) over (partition by dea.location order by dea.location, dea.date ) as RollingPeopleVaccinated
from CovidDeaths dea
join CovidVaccinations vac
on dea.location = vac.location
and dea.date = vac.date
where dea.continent is not null

select * from PercentPopulationVaccinated

