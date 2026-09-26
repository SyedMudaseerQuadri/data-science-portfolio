const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(entry.isIntersecting)entry.target.classList.add("is-visible")})},{threshold:.08});
document.querySelectorAll(".project,.process-step,.skill-cloud span,.facts > div").forEach(el=>{el.style.opacity="0";el.style.transform="translateY(16px)";el.style.transition="opacity .7s ease,transform .7s ease";observer.observe(el)});
const style=document.createElement("style");style.textContent=".is-visible{opacity:1!important;transform:none!important}";document.head.appendChild(style);
