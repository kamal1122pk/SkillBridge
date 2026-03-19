let currentStep = 1;
const totalSteps = 10;

let profileData = {
  name: '',
  headline: '',
  department: '',
  skills: '',
  experience: '',
  stipend: '',
  bank_account: '',
  account_name: '' 
};

document.addEventListener("DOMContentLoaded", () => {
  const profileSuccess = sessionStorage.getItem('profileSuccess');
  console.log("profileSuccess", profileSuccess);
  if (profileSuccess) {
    showToast("Profile and Portfolio Updated Successfully!", "success");
    window.location.href = "freelancerDashboard.html";
  }
});

function getEl(id) { return document.getElementById(id); }
function getValue(id) { return getEl(id)?.value.trim() || ''; }

function showStep(step) {
  for (let i = 1; i <= totalSteps; i++) getEl(`step${i}`).classList.add('hidden');
  getEl(`step${step}`).classList.remove('hidden');
}

async function saveData(step) {
  switch (step) {
    case 1: profileData.name = getValue('name'); break;
    case 3: profileData.headline = getValue('headline'); break;
    case 4: profileData.department = getValue('department'); break;
    case 5:
      // Backend expects an array for skills
      profileData.skills = getValue('skills').split(',').map(s => s.trim()).filter(s => s !== "");
      break;
    case 6: profileData.experience = getValue('experience'); break;
    case 9: profileData.stipend = getValue('stipend'); break;
    case 10: 
      profileData.bank_account = getValue('bankAccount'); 
      profileData.account_name = getValue('accountName');
      break;
  }
}

function validateStep(step) {
  let message = '';
  switch (step) {
    case 1: if (!getValue('name')) message = 'Please enter your name.'; break;
    case 2: if (!getEl('profilePic')?.files[0]) message = 'Please upload a valid image.'; break;
    case 3: if (!getValue('headline')) message = 'Please enter a headline.'; break;
    case 4: if (!getValue('department')) message = 'Please select your department.'; break;
    case 5: if (!getValue('skills')) message = 'Please enter your skills.'; break;
    case 6: if (!getValue('experience')) message = 'Please describe your experience.'; break;
    case 7:
      const imgs = getEl('bestWorkImages')?.files || [];
      if (imgs.length === 0 || imgs.length > 3) message = 'Upload 1-3 images only.';
      break;
    case 8:
      const vid = getEl('videoFile')?.files[0];
      if (!vid) message = 'Please upload a portfolio video.';
      break;
    case 9: if (!getValue('stipend')) message = 'Please enter expected stipend.'; break;
    case 10: 
      if (!getValue('bankAccount')) message = 'Please enter Easypaisa number.'; 
      else if (!getValue('accountName')) message = 'Please enter account name.';
      break;
  }
  if (message) { showToast(message, "warning"); return false; }
  return true;
}

async function nextStep(step) {
  if (!validateStep(step)) return;
  await saveData(step);
  if (step < totalSteps) { currentStep = step + 1; showStep(currentStep); }
}

function prevStep(step) { if (step > 1) { currentStep = step - 1; showStep(currentStep); } }

async function createProfile() {
  sessionStorage.setItem('profileSuccess', true);
  console.log(sessionStorage.getItem('profileSuccess'));
  if (!validateStep(10)) return;
  await saveData(10);

  const btn = document.querySelector("#step10 button");
  const originalText = btn.innerText;

  const token = localStorage.getItem("access_token");
  const userEmail = localStorage.getItem("loggedInUser");

  if (!token || !userEmail) {
    showToast("You need to login first.", "error");
    window.location.href = "login.html";
    return;
  }

  // Effect: Show loading
  btn.innerText = "Finalizing Profile...";
  btn.disabled = true;

  const formData = new FormData();

  // Clean up profileData and append
  formData.append('name', profileData.name);
  formData.append('headline', profileData.headline);
  formData.append('department', profileData.department);
  formData.append('skills', JSON.stringify(profileData.skills));
  formData.append('experience', profileData.experience);
  formData.append('stipend', profileData.stipend);
  formData.append('bank_account', profileData.bank_account);
  formData.append('account_name', profileData.account_name);
  formData.append('is_completed', 'true'); // MARK AS COMPLETED

  // Append profile picture
  const pic = getEl('profilePic')?.files[0];
  if (pic) formData.append('profile_pic', pic);

  try {
    // Use PATCH because registration already created the profile object
    const response = await fetch(`${window.CONFIG.API_BASE_URL}/api/profiles/me/`, {
      method: "PATCH",
      headers: {
        "Authorization": "Bearer " + token,
      },
      body: formData
    });

    if (response.ok) {
      const updatedProfile = await response.json();

      // --- UPLOAD PORTFOLIO MEDIA ---
      // Upload Images
      const imageFiles = getEl('bestWorkImages')?.files || [];
      for (let i = 0; i < imageFiles.length; i++) {
        const imgFormData = new FormData();
        imgFormData.append('file', imageFiles[i]);
        imgFormData.append('media_type', 'image');
        imgFormData.append('profile_email', userEmail);

        await fetch(`${window.CONFIG.API_BASE_URL}/api/portfolio-media/`, {
          method: "POST",
          headers: { "Authorization": "Bearer " + token },
          body: imgFormData
        });
      }

      // Upload Video
      const videoFile = getEl('videoFile')?.files[0];
      if (videoFile) {
        const vidFormData = new FormData();
        vidFormData.append('file', videoFile);
        vidFormData.append('media_type', 'video');
        vidFormData.append('profile_email', userEmail);

        await fetch(`${window.CONFIG.API_BASE_URL}/api/portfolio-media/`, {
          method: "POST",
          headers: { "Authorization": "Bearer " + token },
          body: vidFormData
        });
      }

      // showToast("Profile and Portfolio Updated Successfully!", "success");
      // console.log("Profile and Portfolio Updated Successfully!");
      // sessionStorage.setItem('profileSuccess', true);
      // console.log(sessionStorage.getItem('profileSuccess'));
      window.location.href = "freelancerDashboard.html";

    } else {
      const errors = await response.json();
      showToast("Error creating profile: " + JSON.stringify(errors.error || errors), "error");
      btn.innerText = originalText;
      btn.disabled = false;
    }
  } catch (err) {
    showToast("Network error during profile creation.", "error");
    console.error(err);
    btn.innerText = originalText;
    btn.disabled = false;
  }
}

showStep(1);
