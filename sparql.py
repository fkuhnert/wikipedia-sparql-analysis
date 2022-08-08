from functools import reduce
import requests
import json

url = "https://dbpedia.org/sparql"


def query(depth, t, limit):
    return '''select ?link ?direct_links (count(?other_link) as ?indirect_links) where {
  ?link dbo:wikiPageWikiLink{1,''' + str(depth) + '''} ?other_link .
  { select ?link (count(?other_link2) as ?direct_links) where {
    ?link a ''' + t + ''' .
    ?link dbo:wikiPageWikiLink ?other_link2 .
  } group by ?link order by desc(?direct_links) LIMIT ''' + str(limit) + '''}
} group by ?link ?direct_links order by desc(?indirect_links)
'''


types = ["dbo:Company", "dbo:Activity", "dbo:Name", "dbo:Person", "dbo:Actor", "dbo:Place", "dbo:Publisher", "dbo:Genre", "dbo:Language", "dbo:Department", "dbo:Software", "dbo:School", "dbo:Type", "dbo:AutomobileEngine", "dbo:BaseballSeason", "dbo:Device", "dbo:Engine", "dbo:FootballLeagueSeason", "dbo:FootballMatch", "dbo:GolfTournament", "dbo:GovernmentAgency", "dbo:GrandPrix", "dbo:Library", "dbo:MilitaryStructure", "dbo:MotorsportSeason", "dbo:Mountain", "dbo:NCAATeamSeason", "dbo:NationalFootballLeagueSeason", "dbo:Olympics", "dbo:Outbreak", "dbo:PowerStation", "dbo:RugbyLeague", "dbo:SoccerClubSeason", "dbo:SportsSeason", "dbo:TennisTournament", "dbo:YearInSpaceflight", "dbo:Academic", "dbo:AcademicJournal", "dbo:AdministrativeRegion", "dbo:Airport", "dbo:Album", "dbo:AmericanFootballPlayer", "dbo:AmusementParkAttraction", "dbo:Anime", "dbo:Artist", "dbo:ArtistDiscography", "dbo:Artwork", "dbo:Asteroid", "dbo:Automobile", "dbo:Award", "dbo:Band", "dbo:Bank", "dbo:BasketballTeam", "dbo:Beverage", "dbo:BodyOfWater", "dbo:Book", "dbo:Bridge", "dbo:Building", "dbo:BusCompany", "dbo:ChemicalCompound", "dbo:City", "dbo:CityDistrict", "dbo:ClassicalMusicComposition", "dbo:ComedyGroup", "dbo:Comic", "dbo:ComicsCharacter", "dbo:Convention", "dbo:Criminal", "dbo:CultivatedVariety", "dbo:CyclingRace", "dbo:CyclingTeam",
         "dbo:Disease", "dbo:Drug", "dbo:Earthquake", "dbo:Election", "dbo:Enzyme", "dbo:EthnicGroup", "dbo:EurovisionSongContestEntry", "dbo:Event", "dbo:Film", "dbo:FilmFestival", "dbo:Food", "dbo:Game", "dbo:HistoricBuilding", "dbo:HistoricPlace", "dbo:HockeyTeam", "dbo:Holiday", "dbo:HorseRace", "dbo:Hospital", "dbo:Hotel", "dbo:HumanGene", "dbo:InformationAppliance", "dbo:Lake", "dbo:Legislature", "dbo:Magazine", "dbo:Manga", "dbo:MilitaryConflict", "dbo:MilitaryUnit", "dbo:Monument", "dbo:Museum", "dbo:Musical", "dbo:MusicalArtist", "dbo:Newspaper", "dbo:Organisation", "dbo:Pandemic", "dbo:Park", "dbo:PersonFunction", "dbo:Pharaoh", "dbo:Philosopher", "dbo:Planet", "dbo:Plant", "dbo:Play", "dbo:PoliticalFunction", "dbo:PoliticalParty", "dbo:Politician", "dbo:ProgrammingLanguage", "dbo:ProtectedArea", "dbo:Protein", "dbo:RacingDriver", "dbo:RadioHost", "dbo:RadioProgram", "dbo:RadioStation", "dbo:RailwayLine", "dbo:RecordLabel", "dbo:Religious", "dbo:Reptile", "dbo:ResearchProject", "dbo:Restaurant", "dbo:Road", "dbo:RoadJunction", "dbo:RollerCoaster", "dbo:Royalty", "dbo:RugbyClub", "dbo:RugbyPlayer", "dbo:Sales", "dbo:Settlement", "dbo:Ship", "dbo:ShoppingMall", "dbo:SoccerClub", "dbo:SoccerLeague", "dbo:SoccerTournament", "dbo:Song", "dbo:Sound", "dbo:SpaceMission", "dbo:SportsEvent", "dbo:SportsTeamMember"]


def sum_direct(acc, x): return acc+int(x["direct_links"]["value"])
def sum_indirect(acc, x): return acc+int(x["indirect_links"]["value"])


avg_dict = {}

for t in types:
    depth_dict = {}
    for depth in [2, 3]:
        print(f"{t}-{depth}")

        # Definição dos parâmetros da query
        params = {
            "default-graph-uri": "http://dbpedia.org",
            "query": query(depth, t, 2),
            "format": "application/sparql-results+json"
        }

        # Realização da chamada HTTP
        response = requests.get(url=url, params=params)
        # print(response.content)

        # Tenta fazer o parse o json
        try:
            results = json.loads(response.content)
        except:
            depth_dict[depth] = "-"
            print("Error parsing json")
            continue

        # Calcula o total
        total_direct = reduce(sum_direct, results["results"]["bindings"], 0)
        total_indirect = reduce(
            sum_indirect, results["results"]["bindings"], 0)

        # Realiza a média de links desse tipo
        avg_direct = round(
            total_direct/len(results["results"]["bindings"]), 1) if total_direct > 0 else 0
        avg_indirect = round(
            total_indirect/len(results["results"]["bindings"]), 1) if total_indirect > 0 else 0

        depth_dict[1] = avg_direct
        depth_dict[depth] = avg_indirect
    avg_dict[t] = depth_dict

# print(avg_dict)
print()
print("rdfs:type - 1 - 2 - 3")
for key, res in avg_dict.items():
    print(f"{key} - {res}")

headers = ["rdfs:type", "depth_1", "depth_2"]
headers += ["depth_3"]  # Comentar essa linha caso não queira depth 3

with open(f"results.csv", "w") as file:
    file.write(",".join(headers)+"\n")
    for key, res in avg_dict.items():
        file.write(f"{key},")
        for depth, avg in res.items():
            if depth != len(headers)-1:
                file.write(f"{avg},")
            else:
                file.write(f"{avg}\n")
