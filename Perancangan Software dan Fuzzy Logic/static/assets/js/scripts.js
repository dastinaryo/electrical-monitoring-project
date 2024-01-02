
var currentDate = new Date();
var tanggal = currentDate.getDate().toString().padStart(2, '0') + "-" + (currentDate.getMonth() + 1).toString().padStart(2, '0') + "-" + currentDate.getFullYear();
var timeStamp = currentDate.getHours().toString().padStart(2, '0') + ":" + currentDate.getMinutes().toString().padStart(2, '0') + ":" + currentDate.getSeconds().toString().padStart(2, '0');
var temp_tanggal = tanggal;
// console.log(tanggal)
var hasil = document.querySelector('[data-firebase="hasil"]');

// Mendapatkan referensi ke database
var database = firebase.database();
var dataRef = database.ref("/collection_data/electricity data/"+tanggal);
var dataRef_tms = database.ref("/collection_data/electricity data/"+tanggal+"/timestamp");
var htmlCheckDevice = `Device <a style="padding:0px 5px; background-color:#F54C48; border-radius:10px;"> Disconnected </a>`;

dataRef.once("value", (snapshot) => {
    // currentDate = new Date();
    // timeStamp = currentDate.getHours().toString().padStart(2, '0') + ":" + currentDate.getMinutes().toString().padStart(2, '0') + ":" + currentDate.getSeconds().toString().padStart(2, '0');
    const data_temp = snapshot.val();

});


function interval_check(){
    currentDate = new Date();
    tanggal = currentDate.getDate().toString().padStart(2, '0') + "-" + (currentDate.getMonth() + 1).toString().padStart(2, '0') + "-" + currentDate.getFullYear();
    timeStamp = currentDate.getHours().toString().padStart(2, '0') + ":" + currentDate.getMinutes().toString().padStart(2, '0') + ":" + currentDate.getSeconds().toString().padStart(2, '0');
    
    if (temp_tanggal != tanggal){
    temp_tanggal = tanggal;
    database = firebase.database();
    dataRef = database.ref("/collection_data/electricity data/"+tanggal);
    dataRef_tms = database.ref("/collection_data/electricity data/"+tanggal+"/timestamp");
    }

    database.ref("/collection_data/electricity data/"+tanggal+"/timestamp").once("value", (snapshot) => {
        var checkDevice = document.querySelector('[data-firebase="check-device"]');
        var current_date = snapshot.val();

        // Split the formatted date string into hours, minutes, and seconds
        const [hours_web, minutes_web, seconds_web] = timeStamp.split(':').map(Number);
        const [hours_dev, minutes_dev, seconds_dev] = current_date.split(':').map(Number);


        // Calculate the total seconds
        const totalSeconds_web = hours_web * 3600 + minutes_web * 60 + seconds_web;
        const totalSeconds_dev = hours_dev * 3600 + minutes_dev * 60 + seconds_dev;

        // console.log("Web "+ totalSeconds_web)
        // console.log("Dev "+ (totalSeconds_dev+ 25))


        if (totalSeconds_web > totalSeconds_dev + 25){
        htmlCheckDevice = `Device <a style="padding:0px 5px; background-color:#F54C48; border-radius:10px;"> Disconnected </a>`;
        }else{
        htmlCheckDevice = `Device <a style="padding:0px 5px; background-color:#2DCEA3; border-radius:10px;"> Connected </a>`;
        }


        // current_date = current_date.split(":");

        // var jam = current_date[0];
        // var menit = current_date[1];
        // var detik = current_date[2];
        
        // if (parseInt(currentDate.getHours().toString().padStart(2, '0')) >= parseInt(jam)){
        //   if (parseInt(currentDate.getMinutes().toString().padStart(2, '0')) >= parseInt(menit)){
        //     if (parseInt(currentDate.getSeconds().toString().padStart(2, '0')) >= parseInt(detik)+30){
        //       console.log("Disconnect Detik"+(parseInt(detik)+30))
        //       console.log("Disconnect Detik"+parseInt(currentDate.getSeconds().toString().padStart(2, '0')))
        //       htmlCheckDevice = `Device Disconnected`;
        //     }else{
        //       console.log("Connect Detik"+parseInt(detik))
        //       console.log("Connect Detik"+parseInt(currentDate.getSeconds().toString().padStart(2, '0')))
        //       htmlCheckDevice = `Device Connected`;
        //     }
        //     // htmlCheckDevice = `Device Disconnected`;
        //   }else{
        //     htmlCheckDevice = `Device Connected`;
        //   }
        // }else{
        //   htmlCheckDevice = `Device Connected`;
        // }
        checkDevice.innerHTML = `${htmlCheckDevice}`;
    });
}

setInterval(interval_check, 1000);

// dataRef_tms.on("value", (snapshot) => {
//     // Update data to firebase
//     // console.log(parseInt(temp_biaya));
//     firebase.database().ref("/collection_data/electricity data/"+tanggal).update({
//         "biaya" : parseInt(hitung_biaya(data.daya, data.kwh))
//     })

//     // var checkDevice = document.querySelector('[data-firebase="check-device"]');
//     // var current_date = snapshot.val();

//     // let jam = current_date[0].split(":");
//     // let menit = current_date[1].split(":");
//     // let detik = current_date[2].split(":");
//     // let htmlCheckDevice = `Device Disconnect`;

//     // if (parseInt(currentDate.getHours().toString().padStart(2, '0')) >= parseInt(jam)){
//     //   if (parseInt(currentDate.getMinutes().toString().padStart(2, '0')) >= parseInt(menit)){
//     //     if (parseInt(currentDate.getSeconds().toString().padStart(2, '0')) >= parseInt(detik) +20){
//     //       htmlCheckDevice = `Device Disconnect`;
//     //     }else{
//     //       htmlCheckDevice = `Device Connected`;
//     //     }
//     //   }
//     // }

//     // checkDevice.innerHTML = `${htmlCheckDevice}`;
// });



// Mendapatkan data satu kali (once)
dataRef.on("value", (snapshot) => {
    // currentDate = new Date();
    // timeStamp = currentDate.getHours().toString().padStart(2, '0') + ":" + currentDate.getMinutes().toString().padStart(2, '0') + ":" + currentDate.getSeconds().toString().padStart(2, '0');
    const data = snapshot.val();

    // Cek apakah data ada atau tidak
    if (data) {
        // console.log("masuk if 1");
        if (data.biaya>=0){
            // console.log("ini biaya awal:" + data.biaya);
            firebase.database().ref("/collection_data/electricity data/"+tanggal).update({
                "biaya" : parseInt(hitung_biaya(data.daya, data.kwh))
            })
        } else{
            // console.log("masuk else 2");
            // Jika data tidak ada, maka akan set biaya 0
            firebase.database().ref("/collection_data/electricity data/"+tanggal).set({
                "biaya" : 0,
                "daya" : 0.0,
                "kwh" : 0.0,
                "timestamp" : "00:00:00"
            })
        }
    } else {
        // console.log("masuk else 1");
        // Jika data tidak ada, maka akan set biaya 0
        firebase.database().ref("/collection_data/electricity data/"+tanggal).set({
            "biaya" : 0,
            "daya" : 0.0,
            "kwh" : 0.0,
            "timestamp" : "00:00:00"
        })
    }
});

function hitung_biaya(daya, kwh){
    if (daya <= 900){
        return kwh * 1352}
    else if (daya <= 1300 || daya <= 2200){
        return kwh * 1467}
    else if (daya <= 3500 || daya <= 5500){
        return kwh * 1699}
}