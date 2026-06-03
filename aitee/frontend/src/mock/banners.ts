import type { Banner } from '@/types'
import { bannerImage } from '@/utils/placeholder'

export const banners: Banner[] = [
  {
    id: 1,
    title: '29 元帆布包',
    subtitle: '100% 免费送',
    cta: '立即领取',
    imageUrl: '/assets/img/home/hero.png',
    link: '/gallery',
    location: 'home_top',
  },
  {
    id: 2,
    title: '邀请好友助力',
    subtitle: '29 元帆布包免费送',
    cta: '去领取',
    imageUrl: bannerImage({
      title: '邀请好友',
      subtitle: '29 元帆布包免费送',
      bg: ['#DCFCE7', '#A7F3D0'],
      cta: '去领取',
    }),
    link: '/coupon',
    location: 'mine_invite',
  },
]
