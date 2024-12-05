

function getStorage() {
  // [START storage_create_ref]
  // Get a reference to the storage service, which is used to create references in your storage bucket
  var storage = firebase.storage();

  // Create a storage reference from our storage service
  var storageRef = storage.ref();
  return storageRef;
  // [END storage_create_ref]
}

function downloadViaUrl(url) {
  const storageRef = firebase.storage().ref();

  // [START storage_download_via_url]
  return storageRef.child(url).getDownloadURL()
  // [END storage_download_via_url]
}