const filesInput = document.getElementById('clippings');
const fileInput = document.getElementById('clipping');
filesInput.addEventListener('change', onUpload, false);
fileInput.addEventListener('change', onUpload, false);

const upload = document.getElementById('upload-area');
upload.addEventListener('drop', onUpload);
upload.addEventListener('dragover', onDragOver);

const upload2 = document.getElementById('upload-area2');
upload2.addEventListener('drop', onUpload);
upload2.addEventListener('dragover', onDragOver);

function onDragOver(event) {
  event.preventDefault();
}

function onUpload(event) {
  // preventing the default action for drop event.
event.preventDefault();
const file = event?.dataTransfer?.files || this?.files;
let finputid = event.target.firstElementChild?.getAttribute('id') || event.target?.getAttribute('id');
let finput = document.getElementById(finputid);
finput.files = file;
if (finputid === 'clipping') {
    handleCrop(event, finput);
} else {
    handleCrop2(event, finput)
}
  
}

/* crop */
const alertBox = document.getElementById('alert-box')
const imageBox = document.getElementById('image-box')
const imageBox2 = document.getElementById('image-box2')
const imageForm = document.getElementById('image-form')
const confirmBtn = document.getElementById('confirm-btn')
const input = document.getElementById('clippings')
 
const csrf = document.getElementsByName('csrfmiddlewaretoken')

function handleCrop2(event, finput){
    imageBox2.innerHTML = ""

    document.querySelector('[name="x-axis1"]').value = "";
    document.querySelector('[name="y-axis1"]').value = "";
    document.querySelector('[name="width1"]').value = "";
    document.querySelector('[name="height1"]').value = "";

    document.querySelector('[name="x-axis2"]').value = "";
    document.querySelector('[name="y-axis2"]').value = "";
    document.querySelector('[name="width2"]').value = "";
    document.querySelector('[name="height2"]').value = "";

    document.querySelector('[name="x-axis3"]').value = "";
    document.querySelector('[name="y-axis3"]').value = "";
    document.querySelector('[name="width3"]').value = "";
    document.querySelector('[name="height3"]').value = "";

    document.querySelector('[name="x-axis4"]').value = "";
    document.querySelector('[name="y-axis4"]').value = "";
    document.querySelector('[name="width4"]').value = "";
    document.querySelector('[name="height4"]').value = "";

    document.querySelector('.preview0').innerHTML = "";
    document.querySelector('.preview1').innerHTML = "";
    document.querySelector('.preview2').innerHTML = "";
    document.querySelector('.preview3').innerHTML = "";

    document.querySelector('.previewThumb0').setAttribute('src', '');
    document.querySelector('.previewThumb1').setAttribute('src', '');
    document.querySelector('.previewThumb2').setAttribute('src', '');
    document.querySelector('.previewThumb3').setAttribute('src', '');

    document.querySelector('.previewThumb0').setAttribute('style', '');
    document.querySelector('.previewThumb1').setAttribute('style', '');
    document.querySelector('.previewThumb2').setAttribute('style', '');
    document.querySelector('.previewThumb3').setAttribute('style', '');

    const files = finput.files
    let url;

    if (files.length > 4){
        alert(`Only four images allowed. ${files.length} selected.`)
    } else if(files.length < 1) {
        alert('No images selected')
    } else {
        for(key in files){
            key = parseInt(key)
            window['img_data'+key] = finput.files[key];
            if (Number.isInteger(key)){
                url = URL.createObjectURL(finput.files[key])
                window['url'+key] = url
            }
        }

        for(key in files){
            key = parseInt(key)
            if (Number.isInteger(key)){
                let src = window['url'+key]
                imageBox2.innerHTML += `<div class='my-3'><img class='cimages' src="${src}" id="image${key}" width="700px"></div>`
                var $image = $('#image'+key)
                window['image'+key] = $('#image'+key);
            }
        }
    }

    var images = document.querySelectorAll('.cimages');
    var cropper2;
    images.forEach((v, i) => {
        cropper2 = new Cropper(images[i], {
            aspectRatio: 1 / 1,
            viewMode: 2,
            dragMode: 'move',
            responsive: false,
            restore: false,
            preview: '.preview'+i,
            crop: function(event) {
                // console.log(event.detail.x);
                document.querySelector('[name="x-axis'+(i+1)+'"]').value = event.detail.x
                // console.log(event.detail.y);
                document.querySelector('[name="y-axis'+(i+1)+'"]').value = event.detail.y
                // console.log(event.detail.width);
                document.querySelector('[name="width'+(i+1)+'"]').value = event.detail.width
                // console.log(event.detail.height);
                document.querySelector('[name="height'+(i+1)+'"]').value = event.detail.height
                // console.log(event.detail.rotate);
                // console.log(event.detail.scaleX);
                // console.log(event.detail.scaleY);

                // test2
                let src0 = document.querySelector('.preview0 > img')?.getAttribute('src') || '';
                let style0 = document.querySelector('.preview0 > img')?.getAttribute('style');
                document.querySelector('.previewThumb0').setAttribute('src', src0)
                document.querySelector('.previewThumb0').setAttribute('style', style0)
                let src1 = document.querySelector('.preview1 > img')?.getAttribute('src') || '';
                let style1 = document.querySelector('.preview1 > img')?.getAttribute('style');
                document.querySelector('.previewThumb1').setAttribute('src', src1)
                document.querySelector('.previewThumb1').setAttribute('style', style1)
                let src2 = document.querySelector('.preview2 > img')?.getAttribute('src') || '';
                let style2 = document.querySelector('.preview2 > img')?.getAttribute('style');
                document.querySelector('.previewThumb2').setAttribute('src', src2)
                document.querySelector('.previewThumb2').setAttribute('style', style2)
                let src3 = document.querySelector('.preview3 > img')?.getAttribute('src') || '';
                let style3 = document.querySelector('.preview3 > img')?.getAttribute('style');
                document.querySelector('.previewThumb3').setAttribute('src', src3)
                document.querySelector('.previewThumb3').setAttribute('style', style3)
            }
        });
    });
}
 

function handleCrop(event, finput) {
    imageBox.innerHTML = ""

    document.querySelector('[name="x-axis"]').value = "";
    document.querySelector('[name="y-axis"]').value = "";
    document.querySelector('[name="width"]').value = "";
    document.querySelector('[name="height"]').value = "";

    document.querySelector('.previewThumb').setAttribute('src', '')

    const files = finput.files
    let url;

    if (files.length < 1) {
        alert('No image selected')
    } else if (files.length === 1) {
        const img_data = finput.files[0]
        url = URL.createObjectURL(img_data)
    }

    if (files.length === 1) {
        imageBox.innerHTML = `<img class="cimage" src="${url}" id="image" width="700px">`
        var $image = $('#image')
    }

    var image = document.querySelectorAll('.cimage');
    var cropper;
    image.forEach((v, i) => {
        cropper = new Cropper(image[i], {
            aspectRatio: 1 / 1,
            viewMode: 2,
            dragMode: 'move',
            responsive: false,
            restore: false,
            preview: '.preview',
            crop: function(event) {
                if(files.length === 1){
                    // console.log(event.detail.x);
                    document.querySelector('[name="x-axis"]').value = event.detail.x
                    // console.log(event.detail.y);
                    document.querySelector('[name="y-axis"]').value = event.detail.y
                    // console.log(event.detail.width);
                    document.querySelector('[name="width"]').value = event.detail.width
                    // console.log(event.detail.height);
                    document.querySelector('[name="height"]').value = event.detail.height
                    // console.log(event.detail.rotate);
                    // console.log(event.detail.scaleX);
                    // console.log(event.detail.scaleY);
                }

                // test
                let src = document.querySelector('.preview > img')?.getAttribute('src');
                let style = document.querySelector('.preview > img')?.getAttribute('style');
                document.querySelector('.previewThumb').setAttribute('src', src)
                document.querySelector('.previewThumb').setAttribute('style', style)
                
            }
        });
    });
}

let pielem = document.querySelector('#pname');
let pselem = document.querySelector('#pslug')
let pselemshow = document.querySelector('#pslugshow')

pielem.addEventListener('change', () => updateSlug(pielem, pselem));
pielem.addEventListener('keydown', () => updateSlug(pielem, pselem));
pielem.addEventListener('keyup', () => updateSlug(pielem, pselem));

pielem.addEventListener('change', () => updateSlug(pielem, pselemshow));
pielem.addEventListener('keydown', () => updateSlug(pielem, pselemshow));
pielem.addEventListener('keyup', () => updateSlug(pielem, pselemshow));

let ielem = document.querySelector('#category_name');
let selem = document.querySelector('#category_slug')
let selemshow = document.querySelector('#category_slugshow')

ielem.addEventListener('change', () => updateSlug(ielem, selem));
ielem.addEventListener('keydown', () => updateSlug(ielem, selem));
ielem.addEventListener('keyup', () => updateSlug(ielem, selem));

ielem.addEventListener('change', () => updateSlug(ielem, selemshow));
ielem.addEventListener('keydown', () => updateSlug(ielem, selemshow));
ielem.addEventListener('keyup', () => updateSlug(ielem, selemshow));

function updateSlug(inputElement, slugElement){
    newValue = inputElement.value.trim().replace(' ', '-').toLowerCase().replace(/(^| +)[!-\/:-@\[-`\{-~]*([^ ]*?)[!-\/:-@\[-`\{-~]*(?=\s|$)/gi, '$1$2'); //
    slugElement.value = URLify(inputElement.value)
}

// handle category add
$('#category-form').on('submit', function(event){
    $(':disabled').each(function(e) {
        $(this).removeAttr('disabled');
    })
    event.preventDefault();
    const formData = new FormData(event.target)
    console.log(formData.get('name'))
    var request = new XMLHttpRequest();
    request.open("POST", "/add/category/");
    request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    request.send(formData);
    request.onload = (e) => {
        let categories = JSON.parse(request.response).categories
        categories ? document.querySelector('[name="categories"]').innerHTML = "" : document.querySelector('.cat-err').innerHTML = JSON.parse(request.response).error
        categories?.forEach((v,i)=>{
            document.querySelector('[name="categories"]').innerHTML += `<option value="${v.pk}" >${v.fields.name}</option>`;
        });
        categories ? $(".category-modal").modal('toggle') : ''
    }

    request.onabort = (e) => {
        alert('An error occured trying to add new category.')
    }

    request.onerror = (e) => {
        alert('An error occured trying to add new category.')
    }
    $('#category-form')[0].reset()
})
