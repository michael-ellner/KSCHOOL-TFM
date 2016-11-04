var TweetsMap = new Datamap({
    element: document.getElementById('map'),
    scope: 'world',
    done: function(datamap){datamap.svg.selectAll('.datamaps-subunit').on('click', function(geo){ updateTweeterFeedVar(geo.id); })},
    geographyConfig: {
        //highlightBorderColor: '#bada55',
        popupTemplate: function(geography, data) {
         return '<div class="hoverinfo">'+geography.properties.name + '<br />'+ 'Number of tweets: '+ data.n_tweets;
        },
        popupOnHover: true,
        highlightOnHover: false
    },
    fills: {
        defaultFill: '#1f77b4'
    },
    data: {
    }
});



function bubbles(data) {
    TweetsMap.bubbles(data, {
      popupTemplate: function (geo, data) {
            
            return ['<div class="hoverinfo">' +  data.name,
            '<br/>Number of tweets: ' +  data.n_tweets,
            '</div>'].join('');
      }
    }); 

}
 var country_tweets_id;

 function countryINFO(data){
 console.log(data);
 TweetsMap.updateChoropleth(data);
}

function updateTweeterFeedVar(data){
d=country_tweets_id[data].tweetIDs;
console.log(d);
}
