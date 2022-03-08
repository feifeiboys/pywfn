let size=0.5
let space=0.1
points=[]
for(let x=-size;x<size;x+=space){
    for(let y=-size;y<size;y+=space){
        for(let z=-size;z<size;z+=space){
            points.push([x,y,z])
        }
    }
}
console.log(points.length)